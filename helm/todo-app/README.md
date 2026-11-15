# todo-app Helm Chart (GKE)

`compose-prod.yaml`을 GKE에 배포할 수 있도록 만든 Helm 차트입니다.

| compose-prod.yaml | 이 차트 (GKE) |
|---|---|
| `proxy` (Traefik, 포트 80) | GKE Ingress (`ingressClassName: gce`, Google Cloud 외부 HTTP(S) 로드밸런서) |
| `backend` (FastAPI + React 빌드 결과, 포트 3000) | Deployment + Service (기본 LoadBalancer, `backend.service.type`으로 변경) (`templates/backend-*.yaml`) |
| `mysql` (mysql:9.3, `todo-mysql-data` 볼륨) | StatefulSet + PVC (`templates/mysql-statefulset.yaml`) |
| `.env` (비밀번호) | Kubernetes Secret (`templates/secret.yaml`) 또는 기존 Secret |
| Traefik labels (`Host(localhost)`) | Ingress `rules` (`ingress.host`, 비워 두면 모든 호스트) |
| `depends_on: service_healthy` | `wait-for-mysql` init container + 백엔드 DB 연결 재시도 |

## 1. 사전 준비

```bash
gcloud auth login
gcloud config set project ssu-agent-vertex-509708
gcloud container clusters get-credentials <CLUSTER_NAME> --region asia-northeast3

# 이미지 빌드 및 푸시 (Dockerfile의 기본(마지막) 스테이지 = final)
gcloud auth configure-docker asia-northeast3-docker.pkg.dev
docker build -t asia-northeast3-docker.pkg.dev/ssu-agent-vertex-509708/suntaechung-repo/todo-backend:prod .
docker push asia-northeast3-docker.pkg.dev/ssu-agent-vertex-509708/suntaechung-repo/todo-backend:prod
```

GKE 노드 서비스 계정이 같은 프로젝트의 Artifact Registry를 읽을 수 있어야 합니다. 다른 프로젝트라면 `roles/artifactregistry.reader`를 부여하세요.

## 2. 비밀번호 준비

비밀번호는 차트나 git에 넣지 마세요. 두 방법 중 하나를 선택합니다.

**방법 A: 설치 시 `--set`으로 전달**

```bash
helm upgrade --install todo ./helm/todo-app -n todo --create-namespace \
  --set secrets.mysqlRootPassword='<ROOT_PW>' \
  --set secrets.mysqlAppPassword='<APP_PW>'
```

**방법 B: 기존 Secret 사용 (운영 권장)**

```bash
kubectl create namespace todo
kubectl create secret generic todo-db-secret -n todo \
  --from-literal=MYSQL_ROOT_PASSWORD='<ROOT_PW>' \
  --from-literal=MYSQL_APP_PASSWORD='<APP_PW>'
# values에서 secrets.existingSecret=todo-db-secret 로 지정
```

## 3. 설치

비밀번호를 담은 값 파일을 만들 때는 `values-secret.yaml`처럼 이름을 붙이세요. 이 파일은 `.helmignore`에 의해 패키징에서 제외됩니다. 여기에 더해 `.gitignore`에도 `helm/todo-app/values-secret*.yaml`을 추가하는 것을 권장합니다.

```bash
helm upgrade --install todo ./helm/todo-app -n todo --create-namespace \
  -f values-secret.yaml \
  --set ingress.host=todo.example.com \
  --set ingress.staticIpName=todo-ip
```

설치 후 상태 확인:

```bash
kubectl get pods,svc,ingress -n todo
kubectl get ingress todo-todo-app -n todo   # ADDRESS 열에 IP가 나올 때까지 수 분 대기
```

## 4. 고정 IP 및 HTTPS (선택)

```bash
# 고정 외부 IP 예약 (ingress.staticIpName 에 지정)
gcloud compute addresses create todo-ip --global
gcloud compute addresses describe todo-ip --global --format='value(address)'
```

Google 관리형 인증서를 쓰려면 값 파일에 아래를 추가하세요. 인증서는 DNS A 레코드가 해당 IP를 가리킨 뒤에야 발급됩니다.

```yaml
ingress:
  host: todo.example.com
  staticIpName: todo-ip
  managedCertificate:
    enabled: true
    domains:
      - todo.example.com
```

## 5. 주요 값 (values.yaml)

| 키 | 기본값 | 설명 |
|---|---|---|
| `backend.image.repository` / `tag` | Artifact Registry `todo-backend` / `prod` | 백엔드 이미지 |
| `backend.replicaCount` | `2` | 백엔드 Pod 수 |
| `mysql.enabled` | `true` | `false`면 외부 DB 사용 (`externalDatabase.host` 필수) |
| `mysql.persistence.enabled` / `size` | `true` / `10Gi` | MySQL 데이터 PVC |
| `mysql.persistence.storageClassName` | `""` (클러스터 기본, GKE는 `standard-rwo`) | 스토리지 클래스 |
| `database.name` / `appUser` | `todos` / `todo_app` | compose의 `MYSQL_DATABASE` / `MYSQL_APP_USER` |
| `secrets.existingSecret` | `""` | 키 `MYSQL_ROOT_PASSWORD`, `MYSQL_APP_PASSWORD`를 가진 Secret |
| `ingress.className` | `gce` | GKE 기본 Ingress 컨트롤러 |

## 6. 외부 DB(Cloud SQL)를 쓸 때

`mysql.enabled=false`로 두고 `externalDatabase.host`에 DB 호스트를 넣습니다. Cloud SQL은 보통 Cloud SQL Auth Proxy를 사이드카로 붙여 `127.0.0.1`로 접속하는 방식을 씁니다. 이 차트는 사이드카를 기본 제공하지 않으므로, 필요하면 `backend-deployment.yaml`에 사이드카를 추가하거나 Cloud SQL private IP를 `externalDatabase.host`로 지정하세요.

## 7. 제거

```bash
helm uninstall todo -n todo
kubectl delete pvc data-todo-todo-app-mysql-0 -n todo   # MySQL 데이터까지 지우려는 경우에만 (이름은 kubectl get pvc -n todo 로 확인)
```

`helm uninstall`은 PVC를 삭제하지 않습니다. 데이터가 보존되므로 필요할 때 직접 지우세요.

## 8. 알려진 제약

- MySQL은 단일 replica입니다. 고가용성이 필요하면 Cloud SQL 사용을 검토하세요.
- DB 백업은 이 차트에 포함되지 않습니다.
- 백엔드 이미지는 root로 실행됩니다(Dockerfile 기준). `runAsNonRoot`는 설정하지 않았습니다.
- `helm lint`와 `helm template`으로 렌더링을 검증했습니다. 실제 GKE 클러스터에서의 배포는 아직 확인하지 않았습니다.
