###################################################
# Stage: client-base
#
# This stage is used as the base for the client-dev and client-build stages.
###################################################
FROM node:22-alpine AS client-base
WORKDIR /app/client

COPY client/package.json client/package-lock.json ./
RUN npm install

COPY client/index.html client/vite.config.js client/copy-build.js ./
COPY client/public ./public
COPY client/src ./src

###################################################
# Stage: client-dev
# 
# This stage is used for development of the client application.
###################################################
FROM client-base AS client-dev
EXPOSE 5173
CMD ["npm", "run", "dev"]

###################################################
# Stage: client-build
#
# This stage builds the client application, producing static HTML, CSS, and
# JS files in the dist directory.
###################################################
FROM client-base AS client-build
RUN npm run build


###################################################
################  BACKEND STAGES  #################
###################################################

###################################################
# Stage: backend-base
#
# This stage installs Python dependencies for development and testing.
###################################################
FROM python:3.12-slim AS backend-base
WORKDIR /app/backend

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

###################################################
# Stage: backend-dev
#
# This stage is used for development of the backend FastAPI application.
###################################################
FROM backend-base AS backend-dev
COPY backend/pytest.ini ./
COPY backend/main.py ./
COPY backend/src ./src
COPY backend/spec ./spec

EXPOSE 3000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]

###################################################
# Stage: test
#
# This stage runs the pytest suite on the backend.
# The final stage depends on this stage to guarantee tests pass before image creation.
###################################################
FROM backend-dev AS test
RUN pytest

###################################################
# Stage: final
#
# This stage is the final production image. It copies the FastAPI backend
# and the built React static assets from client-build into src/static.
###################################################
FROM python:3.12-slim AS final
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy requirements from test stage to ensure test stage is executed
COPY --from=test /app/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/main.py ./
COPY backend/src ./src

# Copy built React frontend assets into static folder for FastAPI root serving
COPY --from=client-build /app/client/dist ./src/static

EXPOSE 3000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3000"]