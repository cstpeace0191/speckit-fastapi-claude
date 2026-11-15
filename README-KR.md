# todo-app: Speckit SDLC 진행 및 GKE 배포 가이드

이 문서는 두 부분으로 구성됩니다.

1. **Part 1. Speckit SDLC**: 명세 주도 개발 과정을 설치부터 구현까지 진행하는 방법
2. **Part 2. GKE 배포**: 컨테이너 이미지를 Artifact Registry에 올리고 Helm으로 GKE에 배포하는 방법

> 이 저장소(`Speckit-FastAPI-Claude`)에는 이미 `.specify/`, `specs/001-todo-list-app/`, 백엔드·프론트엔드 코드가 있습니다. Part 1의 `specify init`을 이 저장소 안에서 다시 실행하면 기존 파일이 덮어써질 수 있습니다. Part 1은 **새 폴더**에서 처음부터 진행할 때의 절차로 보세요.

---

## Part 1. Speckit SDLC

### 1-1. Specify CLI 설치

```bash
uv tool install specify-cli
```

`uv`가 없다면 먼저 설치하세요(https://docs.astral.sh/uv/).

### 1-2. 프로젝트 초기화

사용하는 AI 도구에 맞춰 `--integration` 값을 고릅니다.

| 사용하는 도구 | `--integration` 값 |
|---|---|
| Antigravity | `agy` |
| GitHub Copilot | `github` |
| Claude | `claude` |

```bash
specify init <Your Folder Name> --integration claude
cd <Your Folder Name>
```

### 1-3. 헌법(Constitution) 작성

Claude Code 세션을 이 폴더에서 열고 아래 명령을 실행합니다. 헌법 원문은 `constitution-KR.txt`입니다.

```text
/speckit-constitution @constitution-KR.txt
```

### 1-4. 명세(Specify)

요구사항 원문 `requirement-KR.txt`를 입력으로 명세를 만듭니다.

```text
/speckit-specify @requirement-KR.txt
```

### 1-5. 이후 SDLC 단계

아래 순서대로 실행합니다. 각 단계의 산출물은 `specs/<feature>/` 아래에 쌓입니다.

| 순서 | 명령 | 목적 |
|---|---|---|
| 1 | `/speckit-clarify` | 명세의 모호한 부분을 질문으로 좁히고 답을 명세에 반영 |
| 2 | `/speckit-plan` | 구현 계획(plan.md, research.md, data-model.md 등) 작성 |
| 3 | `/speckit-checklist` | 요구사항 품질 체크리스트 작성 |
| 4 | `/speckit-tasks` | 의존 순서가 있는 작업 목록(tasks.md) 생성 |
| 5 | `/speckit-analyze` | spec, plan, tasks 사이의 일관성 점검 (읽기 전용) |
| 6 | `/speckit-implement` | tasks.md의 작업을 순서대로 구현 |
| 7 | `/speckit-converge` | 명세 대비 구현 현황을 평가하고, 빠진 작업을 tasks.md에 추가 |

`/speckit-converge` 후 새 작업이 추가되었다면 `/speckit-implement`를 한 번 더 실행합니다.

---

## Part 2. GKE 배포

이 파트의 값은 현재 강사의 GCP 및 GKE 환경 예시입니다. 다른 프로젝트나 클러스터를 쓰면 아래 변수를 바꿔서 사용하세요.

| 항목 | 값 |
|---|---|
| GCP 프로젝트 ID | `ssu-agent-vertex-509708` |
| 리전 / 존 | `asia-northeast3` / `asia-northeast3-a` |
| GKE 클러스터 이름 | `suntaechung-k8s-cluster` |
| Artifact Registry 저장소 | `suntaechung-repo` (Docker 형식) |
| 이미지 경로 | `asia-northeast3-docker.pkg.dev/ssu-agent-vertex-509708/suntaechung-repo/todo-backend:prod` |
| Helm 릴리스 이름 | `my-helm-getting-started-todo-app` |
| 네임스페이스 | `todo` |

셸 예시는 bash 기준입니다. Windows PowerShell에서는 줄 끝의 `\` 대신 `` ` ``을 쓰고, 경로 구분자를 `/`로 쓰세요. 백슬래시를 그대로 쓰면 bash에서 `helm\todo-app`이 `helmtodo-app`으로 바뀌어 실패합니다.

### 2-1. 사전 준비: 도구 설치

| 도구 | 용도 | 확인 명령 |
|---|---|---|
| Google Cloud CLI (`gcloud`) | GCP 인증, GKE, Artifact Registry | `gcloud --version` |
| `kubectl` | 클러스터 조작 | `kubectl version --client` |
| GKE 인증 플러그인 | kubectl의 GKE 인증 | `gke-gcloud-auth-plugin --version` |
| Docker Desktop | 이미지 빌드·푸시 | `docker version` |
| Helm v3 | 차트 설치 | `helm version` |

```bash
gcloud components install gke-gcloud-auth-plugin
```

### 2-2. GCP 인증 및 프로젝트 설정

```bash
gcloud auth login
gcloud config set project ssu-agent-vertex-509708
gcloud config get-value project
```

### 2-3. GCP API 활성화

GKE, Artifact Registry, 로드밸런서(Compute Engine)에 필요한 API를 켭니다.

```bash
gcloud services enable \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  compute.googleapis.com
```

### 2-4. Artifact Registry 저장소 준비

저장소가 없을 때만 만듭니다. 이미 있으면 건너뜁니다.

```bash
gcloud artifacts repositories create suntaechung-repo \
  --repository-format=docker \
  --location=asia-northeast3 \
  --description="todo-app images"
```

### 2-5. GKE 클러스터 생성

이미 `suntaechung-k8s-cluster`가 있으면 건너뜁니다. 생성에는 몇 분이 걸리고, 노드 비용이 발생합니다.

```bash
gcloud container clusters create suntaechung-k8s-cluster \
  --zone asia-northeast3-a \
  --num-nodes 2 \
  --machine-type e2-standard-2
```

생성 확인:

```bash
gcloud container clusters list
```

### 2-6. Docker의 Artifact Registry 인증

```bash
gcloud auth configure-docker asia-northeast3-docker.pkg.dev
```

### 2-7. kubectl의 GKE 인증 및 컨텍스트 설정

클러스터 자격 증명을 받으면 kubeconfig에 컨텍스트가 추가되고, kubectl이 이 클러스터를 바라보게 됩니다.

```bash
gcloud container clusters get-credentials suntaechung-k8s-cluster \
  --zone asia-northeast3-a \
  --project ssu-agent-vertex-509708
```

현재 컨텍스트가 올바른지 확인합니다. 정상이라면 `gke_ssu-agent-vertex-509708_asia-northeast3-a_suntaechung-k8s-cluster`가 나옵니다.

```bash
kubectl config current-context
kubectl get nodes
```

다른 클러스터의 컨텍스트가 활성화되어 있다면 전환합니다.

```bash
kubectl config use-context gke_ssu-agent-vertex-509708_asia-northeast3-a_suntaechung-k8s-cluster
```

### 2-8. 컨테이너 이미지 빌드, 태깅, 푸시

프로젝트 루트(`Dockerfile`이 있는 곳)에서 실행합니다.

```bash
# 1) 빌드 (기본 대상은 final 스테이지. test 스테이지가 먼저 실행되어 pytest가 통과해야 빌드됩니다)
docker build -t todo-backend:prod .

# 2) Artifact Registry 경로로 태깅
docker tag todo-backend:prod \
  asia-northeast3-docker.pkg.dev/ssu-agent-vertex-509708/suntaechung-repo/todo-backend:prod

# 3) 푸시
docker push asia-northeast3-docker.pkg.dev/ssu-agent-vertex-509708/suntaechung-repo/todo-backend:prod
```

GKE 노드는 `linux/amd64`입니다. Apple Silicon Mac에서 빌드한다면 다음처럼 플랫폼을 지정하세요.

```bash
docker buildx build --platform linux/amd64 \
  -t asia-northeast3-docker.pkg.dev/ssu-agent-vertex-509708/suntaechung-repo/todo-backend:prod \
  --push .
```

푸시 확인:

```bash
gcloud artifacts docker images list \
  asia-northeast3-docker.pkg.dev/ssu-agent-vertex-509708/suntaechung-repo
```

### 2-9. Helm 차트 확인 및 backend Service 타입 설정

backend Service 타입은 `helm/todo-app/values.yaml`의 `backend.service.type`으로 정합니다. 외부에서 접속하려면 `LoadBalancer`여야 합니다.

**1) values.yaml 확인**

```bash
grep -n -A4 "service:" helm/todo-app/values.yaml
```

출력에 `type: LoadBalancer`가 있으면 다음 단계로 넘어갑니다.

**2) LoadBalancer가 아니면 수정**

`helm/todo-app/values.yaml`을 열어 `backend.service.type`을 다음과 같이 맞춥니다.

```yaml
backend:
  service:
    type: LoadBalancer   # ClusterIP 이면 LoadBalancer 로 수정
```

명령줄에서 덮어쓸 수도 있습니다. 이 경우 `--set backend.service.type=LoadBalancer`를 설치·업그레이드 명령에 추가합니다.

**3) LoadBalancer 타입에 따라 함께 확인할 파라미터**

| 파라미터 | 권장값 | 설명 |
|---|---|---|
| `backend.service.type` | `LoadBalancer` | GCP 외부 네트워크 로드밸런서와 공인 IP 생성. `ClusterIP`면 외부 접속 불가 |
| `backend.containerPort` | `3000` | 컨테이너 포트. Service는 외부 80번을 이 포트로 전달 |
| `backend.replicaCount` | `2` | LoadBalancer 뒤에서 파드 2개로 트래픽 분산 |
| `ingress.enabled` | `true`(기본) 또는 `false` | `true`면 Ingress도 생성되어 진입점이 두 개가 됨. LoadBalancer만 쓰려면 `false` 권장 |
| `ingress.staticIpName` | 비움 | Ingress용 고정 IP 설정. LoadBalancer 서비스의 IP에는 적용되지 않음 |

LoadBalancer 서비스만 쓰려면 설치 시 다음과 같이 Ingress를 끕니다.

```bash
--set ingress.enabled=false
```

**4) 렌더링으로 확인**

```bash
helm lint helm/todo-app --set secrets.mysqlRootPassword=x --set secrets.mysqlAppPassword=x

helm template demo helm/todo-app \
  --set secrets.mysqlRootPassword=x --set secrets.mysqlAppPassword=x \
  | grep -n "type: LoadBalancer"
```

`type: LoadBalancer`가 한 줄 나오면 backend Service가 LoadBalancer로 렌더링된 것입니다.

### 2-10. Helm으로 설치

비밀번호는 저장소나 차트에 넣지 않고, 실행 시 환경 변수로 넘깁니다.

```bash
export MYSQL_ROOT_PASSWORD='<루트 비밀번호>'
export MYSQL_APP_PASSWORD='<앱 사용자 비밀번호>'

helm install my-helm-getting-started-todo-app ./helm/todo-app \
  -n todo --create-namespace \
  --set secrets.mysqlRootPassword="$MYSQL_ROOT_PASSWORD" \
  --set secrets.mysqlAppPassword="$MYSQL_APP_PASSWORD"
```

이미 설치된 릴리스를 바꿀 때는 `helm upgrade`를 씁니다. 이전에 저장된 값을 재사용하려면 `--reuse-values`를 붙입니다.

```bash
helm upgrade my-helm-getting-started-todo-app ./helm/todo-app -n todo --reuse-values
```

이 차트는 Ingress(`ingressClassName: gce`)도 기본으로 만듭니다. LoadBalancer 서비스와 Ingress를 함께 쓰면 진입점이 두 개가 됩니다. 하나만 쓰려면 `--set ingress.enabled=false`를 추가하세요.

### 2-11. 배포 확인

파드, 서비스, 릴리스 상태를 확인합니다.

```bash
helm list -n todo
kubectl get pods -n todo
kubectl rollout status deploy/my-helm-getting-started-todo-app-backend -n todo
```

정상이라면 backend 파드 2개와 MySQL 파드 1개가 `Running`, `1/1`이 됩니다. 처음 기동할 때 backend 파드는 `wait-for-mysql` init container가 끝날 때까지 잠시 `Init` 상태를 거칩니다.

외부 IP를 확인합니다. `EXTERNAL-IP`가 `<pending>`이면 GCP가 IP를 할당하는 중이므로 몇 분 뒤 다시 확인하세요.

```bash
kubectl get svc my-helm-getting-started-todo-app-backend -n todo
```

API와 화면을 확인합니다.

```bash
EXTERNAL_IP=$(kubectl get svc my-helm-getting-started-todo-app-backend -n todo \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl "http://$EXTERNAL_IP/api/greeting"   # {"greeting":"Hello world!"}
```

브라우저에서 `http://<EXTERNAL-IP>/`를 열면 todo 화면이 보입니다.

외부 IP가 준비되기 전이나 공인 IP 없이 확인하려면 port-forward를 쓰세요.

```bash
kubectl port-forward -n todo svc/my-helm-getting-started-todo-app-backend 1234:80
# 브라우저: http://localhost:1234/
```

### 2-12. 코드 변경 후 재배포

1. 이미지를 다시 빌드하고 같은 태그로 푸시합니다(2-8).
2. 파드가 새 이미지를 받도록 재시작합니다. 태그가 같으면 `helm upgrade`만으로는 파드가 바뀌지 않으므로 다음 명령을 씁니다.

```bash
kubectl rollout restart deploy/my-helm-getting-started-todo-app-backend -n todo
kubectl rollout status deploy/my-helm-getting-started-todo-app-backend -n todo
```

차트 템플릿이나 값을 바꿨다면 `helm upgrade ... --reuse-values`를 실행합니다.

### 2-13. 삭제

앱만 제거(MySQL PVC는 남음):

```bash
helm uninstall my-helm-getting-started-todo-app -n todo
```

MySQL 데이터까지 지우려면 PVC를 직접 삭제합니다. 이름은 `kubectl get pvc -n todo`로 확인하세요.

```bash
kubectl delete pvc -n todo data-my-helm-getting-started-todo-app-mysql-0
```

클러스터 전체를 지우려면 다음 명령을 씁니다. 되돌릴 수 없고 클러스터 안의 모든 것이 사라집니다.

```bash
gcloud container clusters delete suntaechung-k8s-cluster --zone asia-northeast3-a
```

---

## 부록: 자주 나는 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `non-absolute URLs should be in form of repo_name/path_to_chart, got: helmtodo-app` | bash에서 백슬래시 경로 사용 | `./helm/todo-app`처럼 `/` 사용 |
| `services "...-backend" not found` | 네임스페이스 누락 | `-n todo` 추가 또는 `kubectl config set-context --current --namespace=todo` |
| 파드가 `Init:0/1`에서 멈춤 | MySQL 대기 중이거나 init 이미지 문제 | `kubectl logs -n todo <파드> -c wait-for-mysql` 로 확인 |
| `nil pointer evaluating interface {}.type` | `--reuse-values`로 이전 값 재사용 시 새 키 없음 | 차트 최신 버전 사용 (`dig` 기본값 적용됨) |
| `UPGRADE FAILED` 중 `secrets.mysqlAppPassword is required` | 비밀번호 미지정 | `--set secrets.mysqlRootPassword=... --set secrets.mysqlAppPassword=...` 전달 |
| `EXTERNAL-IP`가 계속 `<pending>` | 로드밸런서 프로비저닝 지연 또는 compute API 미활성화 | 2-3의 API 활성화 확인, `kubectl describe svc`의 Events 확인 |
| `kubectl`이 인증 오류 | GKE 인증 플러그인 미설치 | `gcloud components install gke-gcloud-auth-plugin` |
| 이미지 pull 실패 (`denied`, `unauthorized`) | Docker 인증 또는 노드 권한 부족 | 2-6 재실행, 노드 서비스 계정에 `roles/artifactregistry.reader` 부여 |
