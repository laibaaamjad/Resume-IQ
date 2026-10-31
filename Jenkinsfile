// ResumeIQ - Part II containerized build pipeline
// Plugins used: Git, Pipeline, Docker Pipeline, GitHub (webhook trigger), Email Extension
//
// Trigger: GitHub webhook -> http://<EC2-IP>:8080/github-webhook/
// Result : stack from docker-compose.ci.yml up on port 8081, build result
//          emailed to the person who made the push.

pipeline {
    agent any

    triggers {
        githubPush()
    }

    options {
        skipDefaultCheckout()          // checkout is done explicitly with the Git plugin below
        disableConcurrentBuilds()
        timeout(time: 10, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        REPO_URL       = 'https://github.com/laibaaamjad/Resume-IQ.git'
        APP_IMAGE      = 'laibaaamjad/resumeiq:v1'
        COMPOSE        = 'docker compose -f docker-compose.ci.yml -p resumeiq-ci'
        APP_URL        = 'http://localhost:8081'
        PUBLIC_HOST    = '13.51.188.253'      // Elastic IP of the EC2 instance
        // Used only if the commit author's address is hidden (GitHub noreply)
        FALLBACK_EMAIL = 'qasimalik@gmail.com'
    }

    stages {
        stage('Checkout (Git)') {
            steps {
                git branch: 'main', url: "${REPO_URL}"
                script {
                    env.COMMIT_EMAIL  = sh(script: 'git log -1 --pretty=format:%ae', returnStdout: true).trim()
                    env.COMMIT_AUTHOR = sh(script: 'git log -1 --pretty=format:%an', returnStdout: true).trim()
                    env.COMMIT_MSG    = sh(script: 'git log -1 --pretty=format:%s',  returnStdout: true).trim()
                    env.COMMIT_SHA    = sh(script: 'git rev-parse --short HEAD',     returnStdout: true).trim()
                    env.NOTIFY_TO = env.COMMIT_EMAIL.contains('noreply') ? env.FALLBACK_EMAIL : env.COMMIT_EMAIL
                    echo "Commit ${env.COMMIT_SHA} by ${env.COMMIT_AUTHOR} <${env.COMMIT_EMAIL}>: ${env.COMMIT_MSG}"
                }
            }
        }

        stage('Build in container (Docker Pipeline)') {
            steps {
                script {
                    def runtime = docker.image(env.APP_IMAGE)
                    runtime.pull()
                    // Build/verify the fetched code inside the app's runtime container
                    runtime.inside {
                        sh 'python --version'
                        sh 'python -m compileall -q app.py db.py core utils data'
                        sh 'python -c "import db; print(\'db module OK\')"'
                    }
                }
            }
        }

        stage('Deploy (docker compose)') {
            steps {
                withCredentials([file(credentialsId: 'resumeiq-ci-env', variable: 'ENV_FILE')]) {
                    sh '$COMPOSE --env-file "$ENV_FILE" up -d --force-recreate --remove-orphans'
                }
                sh 'docker ps --filter name=resumeiq-ci'
            }
        }

        stage('Health check') {
            steps {
                sh '''
                    for i in $(seq 1 36); do
                        if curl -fs "$APP_URL/_stcore/health" >/dev/null; then
                            echo "ResumeIQ is up on port 8081 (after $((i*5))s)"
                            exit 0
                        fi
                        sleep 5
                    done
                    echo "App did not become healthy"; docker logs --tail 80 resumeiq-ci-app; exit 1
                '''
            }
        }
    }

    post {
        always {
            emailext(
                to: env.NOTIFY_TO ?: env.FALLBACK_EMAIL,
                recipientProviders: [developers(), requestor()],
                subject: "ResumeIQ CI #${env.BUILD_NUMBER}: ${currentBuild.currentResult}",
                mimeType: 'text/html',
                body: """
                    <h3>ResumeIQ pipeline: ${currentBuild.currentResult}</h3>
                    <p><b>Job:</b> ${env.JOB_NAME} #${env.BUILD_NUMBER}<br>
                       <b>Commit:</b> ${env.COMMIT_SHA ?: '-'} &ndash; ${env.COMMIT_MSG ?: '-'}<br>
                       <b>Pushed by:</b> ${env.COMMIT_AUTHOR ?: '-'} &lt;${env.COMMIT_EMAIL ?: '-'}&gt;<br>
                       <b>Duration:</b> ${currentBuild.durationString.replace(' and counting', '')}</p>
                    <p><b>Application:</b> http://${env.PUBLIC_HOST}:8081<br>
                       <b>Build log:</b> <a href="${env.BUILD_URL}console">${env.BUILD_URL}console</a></p>
                """,
                attachLog: true,
                compressLog: true
            )
        }
    }
}
