# Slack Webhook URL 받기까지의 전체 과정

Slack에서 Incoming Webhook URL을 받아 Spring Boot 애플리케이션과 연동하는 전체 과정을 단계별로 안내합니다.

---

## 목차

1. [Slack 워크스페이스 생성](#1-slack-워크스페이스-생성)
2. [Slack App 생성](#2-slack-app-생성)
3. [Incoming Webhooks 활성화](#3-incoming-webhooks-활성화)
4. [Webhook URL 복사 및 저장](#4-webhook-url-복사-및-저장)
5. [Webhook 테스트](#5-webhook-테스트)
6. [Spring Boot 연동](#6-spring-boot-연동)
7. [주요 주의사항](#7-주요-주의사항)
8. [고급 활용 예제](#8-고급-활용-예제)

---

## 1. Slack 워크스페이스 생성

이미 Slack 계정과 워크스페이스가 있다면 이 단계를 건너뛰세요.

### 회원가입 절차

1. **Slack 웹사이트 접속**
   - URL: https://slack.com
   - "Get Started" 또는 "Sign up" 클릭

2. **이메일 인증**
   - 이메일 주소 입력
   - 받은 인증 코드 확인 및 입력

3. **워크스페이스 설정**
   - 워크스페이스 이름 입력 (예: "DailyFeed Team", "개발팀")
   - 팀원 초대 (선택사항, 나중에도 가능)
   - 채널 생성 (기본 #general, #random 제공)

---

## 2. Slack App 생성

### Slack API 페이지 접속

1. **App 생성 페이지로 이동**
   - URL: https://api.slack.com/apps
   - Slack 계정으로 로그인
   - "Create New App" 버튼 클릭

2. **생성 방식 선택**
   - "From scratch" 선택
   - (또는 "From an app manifest"로 설정 파일 사용 가능)

### 기본 정보 입력

```
App Name: DailyFeed Notifications
(또는 원하는 앱 이름: 예: "시스템 알림", "모니터링 봇")

Pick a workspace to develop your app:
└─ 알림을 받을 워크스페이스 선택
```

3. **"Create App" 클릭**

---

## 3. Incoming Webhooks 활성화

### Webhooks 기능 활성화

1. **Incoming Webhooks 메뉴 접속**
   - 좌측 사이드바에서 "Features" → "Incoming Webhooks" 클릭
   - 또는 "Add features and functionality" → "Incoming Webhooks"

2. **기능 활성화**
   - "Activate Incoming Webhooks" 토글을 **On**으로 변경
   - 페이지가 새로고침되며 추가 옵션이 표시됩니다

### Webhook URL 생성

3. **워크스페이스에 Webhook 추가**
   - 페이지 하단의 "Webhook URLs for Your Workspace" 섹션으로 스크롤
   - "Add New Webhook to Workspace" 버튼 클릭

4. **채널 선택 및 권한 승인**
   - 메시지를 받을 채널 선택
     - 기본 채널: #general
     - 추천: #alerts, #monitoring, #notifications 등 전용 채널 생성
   - "Allow" 버튼 클릭하여 앱에 메시지 전송 권한 부여

---

## 4. Webhook URL 복사 및 저장

### URL 형식

생성된 Webhook URL은 다음과 같은 형식입니다:

```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

- `T00000000`: 워크스페이스 ID
- `B00000000`: 봇/앱 ID
- `XXXXXXXXXXXXXXXXXXXX`: 토큰

### URL 복사 및 관리

1. **URL 복사**
   - "Webhook URL" 옆의 "Copy" 버튼 클릭
   - 또는 수동으로 전체 URL 복사

2. **안전한 저장**
   - ⚠️ **절대 공개 저장소에 커밋하지 마세요**
   - 저장 위치:
     - 로컬 환경변수 파일 (`.env`)
     - Kubernetes Secret
     - AWS Secrets Manager / Azure Key Vault
     - 비밀번호 관리자

---

## 5. Webhook 테스트

### cURL을 사용한 간단한 테스트

#### 기본 텍스트 메시지

```bash
curl -X POST \
  -H 'Content-type: application/json' \
  --data '{"text":"Hello from DailyFeed!"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

#### 성공 응답

```
ok
```

### 풍부한 형식의 메시지 (Block Kit)

```bash
curl -X POST \
  -H 'Content-type: application/json' \
  --data '{
    "blocks": [
      {
        "type": "header",
        "text": {
          "type": "plain_text",
          "text": "🚀 DailyFeed 알림 테스트"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*시스템이 정상적으로 연동되었습니다.*\n\n:white_check_mark: Webhook 연결 성공\n:calendar: 테스트 시간: 2025-01-04"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "context",
        "elements": [
          {
            "type": "mrkdwn",
            "text": "DailyFeed Microservices | Environment: Production"
          }
        ]
      }
    ]
  }' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## 6. Spring Boot 연동

### 6.1 의존성 추가

```xml
<!-- pom.xml -->
<dependencies>
    <!-- Spring Web (RestTemplate 사용) -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- Lombok (선택사항) -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

또는 Gradle:

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
}
```

### 6.2 환경 설정

#### application.yml

```yaml
slack:
  webhook:
    url: ${SLACK_WEBHOOK_URL:https://hooks.slack.com/services/YOUR/WEBHOOK/URL}
    enabled: ${SLACK_ENABLED:true}
  notification:
    channel: "#dailyfeed-alerts"
    username: "DailyFeed Bot"
    icon-emoji: ":robot_face:"
```

#### .env 파일 (로컬 개발용)

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
SLACK_ENABLED=true
```

### 6.3 RestTemplate 설정

```java
package com.dailyfeed.common.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class RestTemplateConfig {
    
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
```

### 6.4 Slack 알림 서비스 구현

#### 기본 구현

```java
package com.dailyfeed.common.notification;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class SlackNotificationService {
    
    private final RestTemplate restTemplate;
    
    @Value("${slack.webhook.url}")
    private String webhookUrl;
    
    @Value("${slack.webhook.enabled:true}")
    private boolean enabled;
    
    /**
     * 간단한 텍스트 메시지 전송
     */
    public void sendMessage(String message) {
        if (!enabled) {
            log.debug("Slack 알림이 비활성화되어 있습니다.");
            return;
        }
        
        try {
            Map<String, Object> payload = Map.of("text", message);
            sendPayload(payload);
            log.info("Slack 메시지 전송 성공: {}", message);
        } catch (Exception e) {
            log.error("Slack 메시지 전송 실패", e);
        }
    }
    
    /**
     * 에러 알림 전송
     */
    public void sendErrorAlert(String serviceName, String errorMessage) {
        if (!enabled) return;
        
        Map<String, Object> payload = Map.of(
            "blocks", List.of(
                Map.of(
                    "type", "header",
                    "text", Map.of(
                        "type", "plain_text",
                        "text", "🚨 시스템 에러 발생",
                        "emoji", true
                    )
                ),
                Map.of(
                    "type", "section",
                    "fields", List.of(
                        Map.of("type", "mrkdwn", "text", "*Service:*\n" + serviceName),
                        Map.of("type", "mrkdwn", "text", "*Time:*\n" + getCurrentTimestamp())
                    )
                ),
                Map.of(
                    "type", "section",
                    "text", Map.of(
                        "type", "mrkdwn",
                        "text", "*Error Message:*\n```" + errorMessage + "```"
                    )
                ),
                Map.of(
                    "type", "divider"
                ),
                Map.of(
                    "type", "context",
                    "elements", List.of(
                        Map.of(
                            "type", "mrkdwn",
                            "text", "DailyFeed Microservices | Environment: Production"
                        )
                    )
                )
            )
        );
        
        sendPayload(payload);
    }
    
    /**
     * 배포 알림 전송
     */
    public void sendDeploymentNotification(String serviceName, String version, String environment) {
        if (!enabled) return;
        
        Map<String, Object> payload = Map.of(
            "blocks", List.of(
                Map.of(
                    "type", "header",
                    "text", Map.of(
                        "type", "plain_text",
                        "text", "🚀 새로운 배포",
                        "emoji", true
                    )
                ),
                Map.of(
                    "type", "section",
                    "fields", List.of(
                        Map.of("type", "mrkdwn", "text", "*Service:*\n" + serviceName),
                        Map.of("type", "mrkdwn", "text", "*Version:*\n" + version),
                        Map.of("type", "mrkdwn", "text", "*Environment:*\n" + environment),
                        Map.of("type", "mrkdwn", "text", "*Deployed At:*\n" + getCurrentTimestamp())
                    )
                ),
                Map.of(
                    "type", "section",
                    "text", Map.of(
                        "type", "mrkdwn",
                        "text", ":white_check_mark: 배포가 성공적으로 완료되었습니다."
                    )
                )
            )
        );
        
        sendPayload(payload);
    }
    
    /**
     * 성능 메트릭 알림 전송
     */
    public void sendPerformanceAlert(String serviceName, String metric, String threshold, String currentValue) {
        if (!enabled) return;
        
        Map<String, Object> payload = Map.of(
            "blocks", List.of(
                Map.of(
                    "type", "header",
                    "text", Map.of(
                        "type", "plain_text",
                        "text", "⚠️ 성능 임계값 초과",
                        "emoji", true
                    )
                ),
                Map.of(
                    "type", "section",
                    "fields", List.of(
                        Map.of("type", "mrkdwn", "text", "*Service:*\n" + serviceName),
                        Map.of("type", "mrkdwn", "text", "*Metric:*\n" + metric),
                        Map.of("type", "mrkdwn", "text", "*Threshold:*\n" + threshold),
                        Map.of("type", "mrkdwn", "text", "*Current Value:*\n" + currentValue)
                    )
                ),
                Map.of(
                    "type", "section",
                    "text", Map.of(
                        "type", "mrkdwn",
                        "text": "*Action Required:* 시스템 성능을 확인하고 필요한 조치를 취하세요."
                    )
                )
            )
        );
        
        sendPayload(payload);
    }
    
    /**
     * Payload 전송 공통 메서드
     */
    private void sendPayload(Map<String, Object> payload) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(payload, headers);
            
            String response = restTemplate.postForObject(webhookUrl, request, String.class);
            
            if (!"ok".equals(response)) {
                log.warn("Slack API 응답이 예상과 다릅니다: {}", response);
            }
        } catch (Exception e) {
            log.error("Slack 알림 전송 실패: {}", e.getMessage(), e);
        }
    }
    
    /**
     * 현재 시간 포맷팅
     */
    private String getCurrentTimestamp() {
        return LocalDateTime.now()
            .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }
}
```

### 6.5 사용 예제

#### Controller에서 사용

```java
package com.dailyfeed.member.controller;

import com.dailyfeed.common.notification.SlackNotificationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/members")
@RequiredArgsConstructor
@Slf4j
public class MemberController {
    
    private final SlackNotificationService slackNotificationService;
    
    @PostMapping
    public ResponseEntity<String> createMember(@RequestBody MemberRequest request) {
        try {
            // 회원 생성 로직
            // ...
            
            // 성공 알림
            slackNotificationService.sendMessage(
                "✅ 새 회원 가입: " + request.getEmail()
            );
            
            return ResponseEntity.ok("Success");
        } catch (Exception e) {
            // 에러 알림
            slackNotificationService.sendErrorAlert(
                "Member Service",
                "회원 생성 실패: " + e.getMessage()
            );
            
            throw e;
        }
    }
}
```

#### Global Exception Handler에서 사용

```java
package com.dailyfeed.common.exception;

import com.dailyfeed.common.notification.SlackNotificationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
@RequiredArgsConstructor
@Slf4j
public class GlobalExceptionHandler {
    
    private final SlackNotificationService slackNotificationService;
    
    @Value("${spring.application.name}")
    private String serviceName;
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleException(Exception e) {
        log.error("Unexpected error occurred", e);
        
        // Slack 알림 전송
        slackNotificationService.sendErrorAlert(
            serviceName,
            e.getClass().getSimpleName() + ": " + e.getMessage()
        );
        
        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("Internal Server Error"));
    }
}
```

#### Scheduled Task에서 사용

```java
package com.dailyfeed.timeline.scheduler;

import com.dailyfeed.common.notification.SlackNotificationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class TimelineCleanupScheduler {
    
    private final SlackNotificationService slackNotificationService;
    
    @Scheduled(cron = "0 0 2 * * *") // 매일 새벽 2시
    public void cleanupOldTimelines() {
        try {
            log.info("타임라인 정리 작업 시작");
            
            // 정리 로직
            int deletedCount = performCleanup();
            
            // 완료 알림
            slackNotificationService.sendMessage(
                String.format("🧹 타임라인 정리 완료: %d개 항목 삭제됨", deletedCount)
            );
            
        } catch (Exception e) {
            slackNotificationService.sendErrorAlert(
                "Timeline Service",
                "타임라인 정리 작업 실패: " + e.getMessage()
            );
        }
    }
    
    private int performCleanup() {
        // 실제 정리 로직
        return 0;
    }
}
```

---

## 7. 주요 주의사항

### 7.1 보안 관련

#### ⚠️ Webhook URL 보안

```bash
# ❌ 절대 하지 말 것
git add application.yml  # Webhook URL이 포함된 파일
git commit -m "Add config"
git push origin main

# ✅ 올바른 방법
# .gitignore에 추가
echo "application-local.yml" >> .gitignore
echo ".env" >> .gitignore
```

#### Kubernetes Secret 사용

```yaml
# slack-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: slack-webhook-secret
  namespace: dailyfeed
type: Opaque
stringData:
  webhook-url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: member-service
spec:
  template:
    spec:
      containers:
      - name: member-service
        env:
        - name: SLACK_WEBHOOK_URL
          valueFrom:
            secretKeyRef:
              name: slack-webhook-secret
              key: webhook-url
```

#### URL 노출 시 대응

1. Slack API 페이지에서 해당 Webhook 삭제
2. 새로운 Webhook URL 생성
3. 모든 서비스의 환경변수 업데이트
4. Git 히스토리에서 민감 정보 제거 (git-filter-repo 사용)

### 7.2 Rate Limiting

#### Slack 제한사항

- **초당 1개 메시지** 제한
- 버스트: 짧은 시간에 여러 메시지 전송 시 429 에러 발생

#### 해결 방안: 메시지 큐잉

```java
package com.dailyfeed.common.notification;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

@Service
@RequiredArgsConstructor
@Slf4j
public class SlackMessageQueue {
    
    private final SlackNotificationService slackService;
    private final BlockingQueue<Map<String, Object>> messageQueue = 
        new LinkedBlockingQueue<>();
    
    public void enqueue(Map<String, Object> payload) {
        try {
            messageQueue.put(payload);
            log.debug("메시지 큐에 추가됨. 현재 큐 크기: {}", messageQueue.size());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            log.error("메시지 큐잉 실패", e);
        }
    }
    
    @Scheduled(fixedDelay = 1000) // 1초마다 실행
    public void processQueue() {
        Map<String, Object> payload = messageQueue.poll();
        if (payload != null) {
            slackService.sendPayload(payload);
        }
    }
}
```

### 7.3 채널 관리

#### 여러 채널에 메시지 보내기

각 채널마다 별도의 Webhook URL이 필요합니다:

```yaml
slack:
  webhooks:
    alerts: ${SLACK_WEBHOOK_ALERTS}      # #alerts 채널
    deployments: ${SLACK_WEBHOOK_DEPLOY} # #deployments 채널
    monitoring: ${SLACK_WEBHOOK_MONITOR}  # #monitoring 채널
```

```java
@Service
public class MultiChannelSlackService {
    
    @Value("${slack.webhooks.alerts}")
    private String alertsWebhook;
    
    @Value("${slack.webhooks.deployments}")
    private String deploymentsWebhook;
    
    @Value("${slack.webhooks.monitoring}")
    private String monitoringWebhook;
    
    public void sendToAlerts(String message) {
        sendToWebhook(alertsWebhook, message);
    }
    
    public void sendToDeployments(String message) {
        sendToWebhook(deploymentsWebhook, message);
    }
    
    // ...
}
```

### 7.4 메시지 포맷팅

#### Markdown 지원

```java
String message = """
    *굵은 글씨*
    _기울임_
    ~취소선~
    `코드`
    ```
    코드 블록
    ```
    > 인용구
    """;
```

#### 링크와 멘션

```java
// 링크
"<https://dailyfeed.com|DailyFeed 대시보드>"

// 사용자 멘션
"<@U12345678> 확인 부탁드립니다."

// 채널 멘션
"<!channel> 중요 공지사항입니다."
"<!here> 온라인 사용자에게 알림"
```

---

## 8. 고급 활용 예제

### 8.1 Interactive 버튼 (Actions)

```java
public void sendInteractiveMessage() {
    Map<String, Object> payload = Map.of(
        "blocks", List.of(
            Map.of(
                "type", "section",
                "text", Map.of(
                    "type", "mrkdwn",
                    "text", "배포를 승인하시겠습니까?"
                )
            ),
            Map.of(
                "type", "actions",
                "elements", List.of(
                    Map.of(
                        "type", "button",
                        "text", Map.of(
                            "type", "plain_text",
                            "text", "승인"
                        ),
                        "style", "primary",
                        "value", "approve"
                    ),
                    Map.of(
                        "type", "button",
                        "text", Map.of(
                            "type", "plain_text",
                            "text", "거부"
                        ),
                        "style", "danger",
                        "value", "reject"
                    )
                )
            )
        )
    );
    
    sendPayload(payload);
}
```

**참고:** Interactive 기능을 사용하려면 Slack App에서 Request URL을 설정해야 합니다.

### 8.2 파일 첨부 (Attachments)

```java
public void sendWithAttachment(String title, String text, String color) {
    Map<String, Object> payload = Map.of(
        "attachments", List.of(
            Map.of(
                "color", color,  // "good", "warning", "danger" 또는 hex color
                "title", title,
                "text", text,
                "footer", "DailyFeed System",
                "ts", System.currentTimeMillis() / 1000
            )
        )
    );
    
    sendPayload(payload);
}
```

### 8.3 Thread Reply (스레드 답글)

```java
public String sendMessage(String message) {
    Map<String, Object> payload = Map.of("text", message);
    // 응답에서 ts (timestamp) 추출하여 반환
    return sendAndGetTimestamp(payload);
}

public void sendThreadReply(String threadTs, String message) {
    Map<String, Object> payload = Map.of(
        "text", message,
        "thread_ts", threadTs
    );
    sendPayload(payload);
}
```

**참고:** Webhook으로는 thread_ts를 직접 받을 수 없습니다. Slack Web API를 사용해야 합니다.

### 8.4 메트릭 대시보드 스타일 메시지

```java
public void sendMetricsDashboard(MetricsData metrics) {
    Map<String, Object> payload = Map.of(
        "blocks", List.of(
            Map.of(
                "type", "header",
                "text", Map.of(
                    "type", "plain_text",
                    "text", "📊 DailyFeed 시스템 메트릭스"
                )
            ),
            Map.of(
                "type", "section",
                "fields", List.of(
                    Map.of("type", "mrkdwn", "text", "*CPU 사용률:*\n" + metrics.getCpuUsage() + "%"),
                    Map.of("type", "mrkdwn", "text", "*메모리:*\n" + metrics.getMemoryUsage() + "MB"),
                    Map.of("type", "mrkdwn", "text", "*활성 사용자:*\n" + metrics.getActiveUsers()),
                    Map.of("type", "mrkdwn", "text", "*요청/분:*\n" + metrics.getRequestsPerMinute())
                )
            ),
            Map.of(
                "type", "divider"
            ),
            Map.of(
                "type", "section",
                "text", Map.of(
                    "type", "mrkdwn",
                    "text", "*서비스 상태:*\n" +
                            "• Member Service: " + getStatusEmoji(metrics.getMemberServiceStatus()) + "\n" +
                            "• Content Service: " + getStatusEmoji(metrics.getContentServiceStatus()) + "\n" +
                            "• Timeline Service: " + getStatusEmoji(metrics.getTimelineServiceStatus())
                )
            )
        )
    );
    
    sendPayload(payload);
}

private String getStatusEmoji(String status) {
    return switch (status) {
        case "UP" -> ":large_green_circle: UP";
        case "DOWN" -> ":red_circle: DOWN";
        default -> ":yellow_circle: UNKNOWN";
    };
}
```

---

## 참고 자료

### Slack 공식 문서

- **Incoming Webhooks**: https://api.slack.com/messaging/webhooks
- **Block Kit Builder**: https://app.slack.com/block-kit-builder
- **Message Formatting**: https://api.slack.com/reference/surfaces/formatting
- **Attachment 필드**: https://api.slack.com/reference/messaging/attachments

### Block Kit 리소스

- **Block Kit 샘플**: https://api.slack.com/block-kit
- **Interactive 컴포넌트**: https://api.slack.com/interactivity
- **Layout Blocks**: https://api.slack.com/reference/block-kit/blocks

### Spring Boot 관련

- **RestTemplate 문서**: https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/client/RestTemplate.html
- **Spring Boot Configuration**: https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.external-config

---

## 문제 해결 (Troubleshooting)

### "Invalid token" 에러

**원인:**
- Webhook URL이 잘못되었거나 만료됨
- URL 복사 시 공백이나 특수문자가 포함됨

**해결:**
1. Webhook URL 재생성
2. URL 복사 시 전체 URL이 정확히 복사되었는지 확인
3. 환경변수에 따옴표나 공백이 없는지 확인

### "No service" 에러

**원인:**
- 해당 Workspace에서 앱이 제거됨
- 앱의 권한이 취소됨

**해결:**
1. Slack Workspace에서 앱이 설치되어 있는지 확인
2. 앱 재설치 또는 권한 재승인

### 메시지가 전송되지 않음

**체크리스트:**
1. Webhook URL이 올바른지 확인
2. 네트워크 연결 확인 (방화벽, 프록시 설정)
3. JSON 형식이 올바른지 확인
4. Rate Limit 초과 여부 확인 (429 에러)
5. 로그에서 예외 메시지 확인

### 한글 깨짐 현상

**해결:**
```java
HttpHeaders headers = new HttpHeaders();
headers.setContentType(MediaType.APPLICATION_JSON);
headers.setAcceptCharset(List.of(StandardCharsets.UTF_8));
```

---

## 마무리

이 가이드를 통해 Slack Webhook을 DailyFeed 마이크로서비스 아키텍처에 통합하여 실시간 알림 시스템을 구축할 수 있습니다.

### 핵심 요약

1. ✅ Slack App 생성 및 Webhook 활성화
2. ✅ Webhook URL 안전하게 관리 (Secret, 환경변수)
3. ✅ Spring Boot에서 RestTemplate로 메시지 전송
4. ✅ Block Kit으로 풍부한 메시지 포맷 활용
5. ✅ Rate Limiting 및 에러 처리 구현

### 추천 사항

- 각 마이크로서비스별 전용 채널 생성
- 중요도별 알림 분류 (Critical, Warning, Info)
- 메시지 템플릿 재사용으로 일관성 유지
- 모니터링 메트릭과 연동하여 자동 알림 설정

---

**작성일:** 2025-01-04  
**버전:** 1.0  
**작성자:** Claude (Anthropic)  
**대상:** DailyFeed Microservices Architecture
