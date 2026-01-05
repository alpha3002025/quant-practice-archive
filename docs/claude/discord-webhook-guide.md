# Discord Webhook 설정 가이드

Discord에서 Webhook URL을 생성하고 Spring Boot 애플리케이션과 연동하는 전체 과정을 단계별로 안내합니다.

---

## 목차

1. [Discord 가입](#1-discord-가입)
2. [서버 생성](#2-서버-생성)
3. [채널 생성](#3-채널-생성)
4. [Webhook 생성](#4-webhook-생성)
5. [Webhook URL 복사](#5-webhook-url-복사)
6. [Webhook 테스트](#6-webhook-테스트)
7. [Spring Boot 연동](#7-spring-boot-연동)
8. [메시지 포맷팅](#8-메시지-포맷팅)
9. [주요 주의사항](#9-주요-주의사항)
10. [고급 활용](#10-고급-활용)

---

## 1. Discord 가입

### Discord 설치

**데스크톱 앱**
- Windows/Mac/Linux: https://discord.com/download
- 브라우저에서도 사용 가능: https://discord.com/app

**모바일 앱**
- iOS: App Store에서 "Discord" 검색
- Android: Google Play에서 "Discord" 검색

### 계정 생성

1. **Discord 웹사이트 접속**
   - URL: https://discord.com
   - "Login" 또는 "Open Discord in your browser" 클릭

2. **회원가입**
   - 이메일 주소 입력
   - 사용자명 입력
   - 비밀번호 설정
   - 생년월일 입력

3. **이메일 인증**
   - 받은 인증 이메일에서 "Verify Email" 클릭
   - Discord 앱 또는 웹으로 로그인

---

## 2. 서버 생성

Discord에서 Webhook을 사용하려면 먼저 서버(Server)를 생성해야 합니다.

### 서버 생성 방법

1. **서버 추가 버튼 클릭**
   - 왼쪽 사이드바 하단의 "+" 아이콘 클릭
   - 또는 "서버 추가" 버튼 클릭

2. **템플릿 선택**
   - "직접 만들기(Create My Own)" 선택
   - 또는 기존 템플릿 사용 가능

3. **서버 용도 선택**
   - "나와 친구들을 위한 서버" 선택
   - 또는 "클럽이나 커뮤니티를 위한 서버" 선택

4. **서버 정보 입력**
   ```
   서버 이름: DailyFeed Notifications
   서버 아이콘: (선택사항)
   ```

5. **서버 생성 완료**
   - "생성" 버튼 클릭
   - 새 서버가 왼쪽 사이드바에 나타납니다

---

## 3. 채널 생성

서버에는 기본적으로 #general 채널이 생성되어 있습니다. 필요에 따라 전용 채널을 추가로 생성할 수 있습니다.

### 채널 생성 방법

1. **채널 추가**
   - 채널 목록 옆의 "+" 아이콘 클릭
   - 또는 서버 이름 우클릭 → "채널 만들기"

2. **채널 타입 선택**
   - 텍스트 채널 (Webhook은 텍스트 채널에만 가능)
   - 음성 채널
   - 공지사항 채널
   - 포럼 채널

3. **채널 정보 입력**
   ```
   채널 이름: alerts
   채널 주제: 시스템 알림 및 모니터링
   비공개 채널: (필요시 체크)
   ```

**추천 채널 구조:**
```
📢 공지사항
  └─ #announcements
  
🔔 알림
  └─ #system-alerts
  └─ #deployment-notifications
  └─ #error-logs
  
📊 모니터링
  └─ #metrics
  └─ #performance
```

---

## 4. Webhook 생성

### Webhook 생성 과정

1. **채널 설정 열기**
   - 알림을 받을 채널 위에서 우클릭
   - "채널 수정(Edit Channel)" 선택

2. **통합 메뉴 접속**
   - 왼쪽 메뉴에서 "통합(Integrations)" 클릭
   - 또는 "Webhooks" 섹션 찾기

3. **새 Webhook 생성**
   - "Webhook 만들기" 또는 "New Webhook" 버튼 클릭
   - Discord가 자동으로 기본 Webhook 생성

4. **Webhook 커스터마이징**
   ```
   이름: DailyFeed Bot
   아바타: (선택사항) 봇 이미지 업로드
   채널: #system-alerts
   ```

5. **저장**
   - "변경 사항 저장" 클릭

---

## 5. Webhook URL 복사

### URL 확인 및 복사

생성된 Webhook에서 "Webhook URL 복사" 버튼을 클릭합니다.

**URL 형식:**
```
https://discord.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyz-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789
```

**URL 구조:**
```
https://discord.com/api/webhooks/{webhook_id}/{webhook_token}
```

- `webhook_id`: Webhook 고유 ID (숫자)
- `webhook_token`: 인증 토큰 (영문자+숫자 조합)

### URL 안전하게 보관

⚠️ **중요: Webhook URL은 절대 공개하지 마세요!**

- GitHub, GitLab 등 공개 저장소에 커밋 금지
- 환경변수나 Secret으로 관리
- URL이 노출되면 즉시 삭제하고 새로 생성

**저장 위치:**
- `.env` 파일
- Kubernetes Secret
- AWS Secrets Manager
- Azure Key Vault

---

## 6. Webhook 테스트

### cURL을 사용한 간단한 테스트

#### 기본 텍스트 메시지

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello from DailyFeed!"}' \
  https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

#### 성공 응답

HTTP 204 No Content (성공 시 빈 응답)

### 풍부한 형식의 메시지 (Embed)

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "username": "DailyFeed Bot",
    "avatar_url": "https://example.com/avatar.png",
    "embeds": [{
      "title": "🚀 시스템 알림",
      "description": "DailyFeed 시스템이 정상적으로 시작되었습니다.",
      "color": 5814783,
      "fields": [
        {
          "name": "환경",
          "value": "Production",
          "inline": true
        },
        {
          "name": "버전",
          "value": "v1.2.3",
          "inline": true
        }
      ],
      "timestamp": "2025-01-04T15:30:00.000Z",
      "footer": {
        "text": "DailyFeed Monitoring"
      }
    }]
  }' \
  https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

### Postman으로 테스트

1. **새 요청 생성**
   - Method: POST
   - URL: Webhook URL 붙여넣기

2. **Headers 설정**
   ```
   Content-Type: application/json
   ```

3. **Body 설정** (raw JSON)
   ```json
   {
     "content": "테스트 메시지입니다."
   }
   ```

4. **Send 버튼 클릭**

---

## 7. Spring Boot 연동

### 7.1 의존성 추가

#### Maven (pom.xml)

```xml
<dependencies>
    <!-- Spring Boot Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- Jackson (JSON 처리) -->
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
    </dependency>
    
    <!-- Lombok -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

#### Gradle (build.gradle)

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'com.fasterxml.jackson.core:jackson-databind'
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
}
```

### 7.2 환경 설정

#### application.yml

```yaml
discord:
  webhook:
    url: ${DISCORD_WEBHOOK_URL:https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN}
    username: ${DISCORD_WEBHOOK_USERNAME:DailyFeed Bot}
    avatar-url: ${DISCORD_WEBHOOK_AVATAR:https://example.com/avatar.png}
  enabled: ${DISCORD_ENABLED:true}
  
  # 여러 채널 사용 시
  webhooks:
    alerts: ${DISCORD_WEBHOOK_ALERTS}
    deployments: ${DISCORD_WEBHOOK_DEPLOYMENTS}
    errors: ${DISCORD_WEBHOOK_ERRORS}
    metrics: ${DISCORD_WEBHOOK_METRICS}
```

#### .env 파일

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1234567890/abcdefghijklmnop
DISCORD_WEBHOOK_USERNAME=DailyFeed Bot
DISCORD_WEBHOOK_AVATAR=https://dailyfeed.com/images/bot-avatar.png
DISCORD_ENABLED=true
```

### 7.3 DTO 정의

#### DiscordWebhookRequest.java

```java
package com.dailyfeed.common.discord.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class DiscordWebhookRequest {
    
    private String content;          // 메시지 내용 (최대 2000자)
    private String username;         // Webhook 사용자명 (Override)
    
    @JsonProperty("avatar_url")
    private String avatarUrl;        // Webhook 아바타 URL (Override)
    
    private Boolean tts;             // Text-to-Speech 활성화
    
    private List<Embed> embeds;      // Embed 메시지 (최대 10개)
    
    @JsonProperty("allowed_mentions")
    private AllowedMentions allowedMentions;
    
    @Data
    @Builder
    public static class Embed {
        private String title;        // 제목 (최대 256자)
        private String description;  // 설명 (최대 4096자)
        private String url;          // 제목 클릭 시 이동할 URL
        private Integer color;       // 왼쪽 색상 바 (Decimal color)
        private String timestamp;    // ISO8601 형식 타임스탬프
        
        private Footer footer;
        private Image image;
        private Thumbnail thumbnail;
        private Author author;
        private List<Field> fields;  // 필드 (최대 25개)
        
        @Data
        @Builder
        public static class Footer {
            private String text;     // 푸터 텍스트 (최대 2048자)
            
            @JsonProperty("icon_url")
            private String iconUrl;  // 푸터 아이콘 URL
        }
        
        @Data
        @Builder
        public static class Image {
            private String url;      // 이미지 URL
        }
        
        @Data
        @Builder
        public static class Thumbnail {
            private String url;      // 썸네일 URL
        }
        
        @Data
        @Builder
        public static class Author {
            private String name;     // 작성자 이름 (최대 256자)
            private String url;      // 작성자 URL
            
            @JsonProperty("icon_url")
            private String iconUrl;  // 작성자 아이콘 URL
        }
        
        @Data
        @Builder
        public static class Field {
            private String name;     // 필드 이름 (최대 256자)
            private String value;    // 필드 값 (최대 1024자)
            private Boolean inline;  // 인라인 표시 여부
        }
    }
    
    @Data
    @Builder
    public static class AllowedMentions {
        private List<String> parse;  // "roles", "users", "everyone"
        private List<String> roles;  // 특정 Role ID 목록
        private List<String> users;  // 특정 User ID 목록
    }
}
```

### 7.4 Discord Webhook Service

```java
package com.dailyfeed.common.discord.service;

import com.dailyfeed.common.discord.dto.DiscordWebhookRequest;
import com.dailyfeed.common.discord.dto.DiscordWebhookRequest.Embed;
import com.dailyfeed.common.discord.dto.DiscordWebhookRequest.Embed.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class DiscordWebhookService {
    
    private final RestTemplate restTemplate;
    
    @Value("${discord.webhook.url}")
    private String webhookUrl;
    
    @Value("${discord.webhook.username:DailyFeed Bot}")
    private String defaultUsername;
    
    @Value("${discord.webhook.avatar-url:}")
    private String defaultAvatarUrl;
    
    @Value("${discord.enabled:true}")
    private boolean enabled;
    
    /**
     * 간단한 텍스트 메시지 전송
     */
    public void sendMessage(String content) {
        if (!enabled) {
            log.debug("Discord 알림이 비활성화되어 있습니다.");
            return;
        }
        
        DiscordWebhookRequest request = DiscordWebhookRequest.builder()
            .content(content)
            .username(defaultUsername)
            .avatarUrl(defaultAvatarUrl)
            .build();
        
        sendWebhook(request);
    }
    
    /**
     * Embed 메시지 전송
     */
    public void sendEmbed(Embed embed) {
        if (!enabled) return;
        
        DiscordWebhookRequest request = DiscordWebhookRequest.builder()
            .username(defaultUsername)
            .avatarUrl(defaultAvatarUrl)
            .embeds(List.of(embed))
            .build();
        
        sendWebhook(request);
    }
    
    /**
     * 에러 알림 전송
     */
    public void sendErrorAlert(String serviceName, String errorMessage) {
        Embed embed = Embed.builder()
            .title("🚨 시스템 에러 발생")
            .description("DailyFeed 시스템에서 에러가 발생했습니다.")
            .color(15158332) // 빨간색 (#E74C3C)
            .fields(List.of(
                Field.builder()
                    .name("Service")
                    .value(serviceName)
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("Time")
                    .value(getCurrentTimestamp())
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("Error Message")
                    .value("```\n" + errorMessage + "\n```")
                    .inline(false)
                    .build()
            ))
            .timestamp(getCurrentIsoTimestamp())
            .footer(Footer.builder()
                .text("DailyFeed Monitoring")
                .build())
            .build();
        
        sendEmbed(embed);
    }
    
    /**
     * 성공 알림 전송
     */
    public void sendSuccessAlert(String title, String message) {
        Embed embed = Embed.builder()
            .title("✅ " + title)
            .description(message)
            .color(3066993) // 초록색 (#2ECC71)
            .timestamp(getCurrentIsoTimestamp())
            .footer(Footer.builder()
                .text("DailyFeed System")
                .build())
            .build();
        
        sendEmbed(embed);
    }
    
    /**
     * 경고 알림 전송
     */
    public void sendWarningAlert(String title, String message) {
        Embed embed = Embed.builder()
            .title("⚠️ " + title)
            .description(message)
            .color(16776960) // 노란색 (#FFFF00)
            .timestamp(getCurrentIsoTimestamp())
            .footer(Footer.builder()
                .text("DailyFeed System")
                .build())
            .build();
        
        sendEmbed(embed);
    }
    
    /**
     * 정보 알림 전송
     */
    public void sendInfoAlert(String title, String message) {
        Embed embed = Embed.builder()
            .title("ℹ️ " + title)
            .description(message)
            .color(3447003) // 파란색 (#3498DB)
            .timestamp(getCurrentIsoTimestamp())
            .footer(Footer.builder()
                .text("DailyFeed System")
                .build())
            .build();
        
        sendEmbed(embed);
    }
    
    /**
     * 배포 알림 전송
     */
    public void sendDeploymentNotification(String serviceName, String version, String environment) {
        Embed embed = Embed.builder()
            .title("🚀 새로운 배포")
            .description("새 버전이 배포되었습니다.")
            .color(5814783) // 보라색 (#58B9FF)
            .fields(List.of(
                Field.builder()
                    .name("Service")
                    .value(serviceName)
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("Version")
                    .value(version)
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("Environment")
                    .value(environment)
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("Deployed At")
                    .value(getCurrentTimestamp())
                    .inline(false)
                    .build()
            ))
            .timestamp(getCurrentIsoTimestamp())
            .footer(Footer.builder()
                .text("DailyFeed Deployment")
                .build())
            .build();
        
        sendEmbed(embed);
    }
    
    /**
     * 시스템 메트릭 알림
     */
    public void sendMetricsAlert(String serviceName, MetricsData metrics) {
        Embed embed = Embed.builder()
            .title("📊 시스템 메트릭스")
            .description("현재 시스템 상태입니다.")
            .color(10181046) // 회색 (#9B59B6)
            .fields(List.of(
                Field.builder()
                    .name("Service")
                    .value(serviceName)
                    .inline(false)
                    .build(),
                Field.builder()
                    .name("CPU Usage")
                    .value(metrics.getCpuUsage() + "%")
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("Memory")
                    .value(metrics.getMemoryUsage() + "MB")
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("Active Users")
                    .value(String.valueOf(metrics.getActiveUsers()))
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("Requests/min")
                    .value(String.valueOf(metrics.getRequestsPerMinute()))
                    .inline(true)
                    .build()
            ))
            .timestamp(getCurrentIsoTimestamp())
            .footer(Footer.builder()
                .text("DailyFeed Metrics")
                .build())
            .build();
        
        sendEmbed(embed);
    }
    
    /**
     * Webhook 전송 (공통 메서드)
     */
    private void sendWebhook(DiscordWebhookRequest request) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<DiscordWebhookRequest> entity = new HttpEntity<>(request, headers);
            
            ResponseEntity<Void> response = restTemplate.exchange(
                webhookUrl,
                HttpMethod.POST,
                entity,
                Void.class
            );
            
            if (response.getStatusCode() == HttpStatus.NO_CONTENT) {
                log.info("Discord 메시지 전송 성공");
            }
        } catch (Exception e) {
            log.error("Discord 메시지 전송 실패: {}", e.getMessage(), e);
        }
    }
    
    /**
     * 현재 시간 포맷팅 (한국 시간)
     */
    private String getCurrentTimestamp() {
        return LocalDateTime.now()
            .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }
    
    /**
     * ISO8601 형식 타임스탬프
     */
    private String getCurrentIsoTimestamp() {
        return LocalDateTime.now()
            .atOffset(ZoneOffset.UTC)
            .format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);
    }
}
```

### 7.5 메트릭 데이터 클래스

```java
package com.dailyfeed.common.discord.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class MetricsData {
    private double cpuUsage;
    private long memoryUsage;
    private int activeUsers;
    private int requestsPerMinute;
}
```

### 7.6 RestTemplate 설정

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

---

## 8. 메시지 포맷팅

### 8.1 Discord Markdown

Discord는 제한적인 Markdown을 지원합니다.

#### 기본 포맷팅

```markdown
*기울임* 또는 _기울임_
**굵게** 또는 __굵게__
***굵은 기울임*** 또는 ___굵은 기울임___
~~취소선~~
__밑줄__
||스포일러||
```

#### 코드 블록

```markdown
`인라인 코드`

```java
// 코드 블록
public void hello() {
    System.out.println("Hello");
}
```
```

#### 인용구

```markdown
> 단일 줄 인용
>>> 여러 줄
인용구
```

#### 리스트

```markdown
- 항목 1
- 항목 2
  - 하위 항목

1. 번호 항목 1
2. 번호 항목 2
```

### 8.2 색상 코드

Embed의 `color` 필드는 Decimal 값을 사용합니다.

**주요 색상:**

```java
public class DiscordColors {
    public static final int DEFAULT = 0;           // #000000
    public static final int AQUA = 1752220;        // #1ABC9C
    public static final int GREEN = 3066993;       // #2ECC71
    public static final int BLUE = 3447003;        // #3498DB
    public static final int PURPLE = 10181046;     // #9B59B6
    public static final int GOLD = 15844367;       // #F1C40F
    public static final int ORANGE = 15105570;     // #E67E22
    public static final int RED = 15158332;        // #E74C3C
    public static final int GREY = 9807270;        // #95A5A6
    public static final int DARKER_GREY = 8359053; // #7F8C8D
    public static final int NAVY = 3426654;        // #34495E
    public static final int DARK_AQUA = 1146986;   // #11806A
    public static final int DARK_GREEN = 2067276;  // #1F8B4C
    public static final int DARK_BLUE = 2123412;   // #206694
    public static final int DARK_PURPLE = 7419530; // #71368A
    public static final int DARK_GOLD = 12745742;  // #C27C0E
    public static final int DARK_ORANGE = 11027200;// #A84300
    public static final int DARK_RED = 10038562;   // #992D22
    public static final int DARK_GREY = 9936031;   // #979C9F
}
```

**Hex to Decimal 변환:**

```java
public static int hexToDecimal(String hex) {
    return Integer.parseInt(hex.replace("#", ""), 16);
}

// 사용 예:
int customColor = hexToDecimal("#FF5733");
```

### 8.3 멘션

```java
// 사용자 멘션
content = "<@USER_ID> 확인해주세요";

// 역할 멘션
content = "<@&ROLE_ID> 공지사항입니다";

// 채널 멘션
content = "<#CHANNEL_ID>에서 확인하세요";

// @everyone
content = "@everyone 중요 공지";

// @here (온라인 사용자만)
content = "@here 긴급 알림";
```

---

## 9. 주요 주의사항

### 9.1 보안

#### Webhook URL 관리

```bash
# ❌ 절대 금지
git add application.yml  # Webhook URL 포함
git commit -m "Add config"
git push

# ✅ 올바른 방법
# .gitignore
application-local.yml
.env
```

#### Kubernetes Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: discord-webhook-secret
  namespace: dailyfeed
type: Opaque
stringData:
  webhook-url: "https://discord.com/api/webhooks/1234567890/abcdefghijk"
```

```yaml
# Deployment
env:
- name: DISCORD_WEBHOOK_URL
  valueFrom:
    secretKeyRef:
      name: discord-webhook-secret
      key: webhook-url
```

#### Webhook URL 노출 시 대응

1. Discord 서버 → 채널 설정 → 통합 → Webhook
2. 해당 Webhook 삭제
3. 새로운 Webhook 생성
4. 모든 환경의 URL 업데이트

### 9.2 Rate Limiting

**Discord Webhook 제한:**
- Webhook당 초당 5개 요청
- 초당 30개 요청 (전체 봇)
- 429 에러 발생 시 Retry-After 헤더 확인

#### Rate Limit 처리

```java
@Service
@Slf4j
public class DiscordWebhookService {
    
    private final Semaphore rateLimiter = new Semaphore(5); // 초당 5개
    
    public void sendWebhookWithRateLimit(DiscordWebhookRequest request) {
        try {
            rateLimiter.acquire();
            sendWebhook(request);
            
            // 200ms 대기 (초당 5개 = 200ms 간격)
            Thread.sleep(200);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            log.error("Rate limiter 인터럽트", e);
        } finally {
            rateLimiter.release();
        }
    }
}
```

#### Retry 로직

```java
public void sendWithRetry(DiscordWebhookRequest request) {
    int maxRetries = 3;
    int retryDelay = 1000;
    
    for (int i = 0; i < maxRetries; i++) {
        try {
            sendWebhook(request);
            return;
        } catch (HttpClientErrorException e) {
            if (e.getStatusCode() == HttpStatus.TOO_MANY_REQUESTS) {
                String retryAfter = e.getResponseHeaders().getFirst("Retry-After");
                int delay = retryAfter != null ? 
                    Integer.parseInt(retryAfter) * 1000 : retryDelay;
                
                log.warn("Rate limit 초과, {}ms 후 재시도", delay);
                Thread.sleep(delay);
                retryDelay *= 2; // Exponential backoff
            } else {
                throw e;
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            break;
        }
    }
}
```

### 9.3 메시지 크기 제한

**Discord 제한사항:**
- `content`: 최대 2000자
- `embed.title`: 최대 256자
- `embed.description`: 최대 4096자
- `embed.field.name`: 최대 256자
- `embed.field.value`: 최대 1024자
- `embed.footer.text`: 최대 2048자
- `embeds`: 최대 10개
- `embed.fields`: 최대 25개
- 전체 Embed: 최대 6000자

#### 긴 메시지 분할

```java
public void sendLongMessage(String longContent) {
    int maxLength = 2000;
    
    if (longContent.length() <= maxLength) {
        sendMessage(longContent);
        return;
    }
    
    List<String> chunks = splitMessage(longContent, maxLength);
    for (String chunk : chunks) {
        sendMessage(chunk);
        try {
            Thread.sleep(200); // Rate limit 고려
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

private List<String> splitMessage(String message, int maxLength) {
    List<String> chunks = new ArrayList<>();
    int length = message.length();
    
    for (int i = 0; i < length; i += maxLength) {
        chunks.add(message.substring(i, Math.min(length, i + maxLength)));
    }
    
    return chunks;
}
```

### 9.4 Webhook 검증 (선택사항)

Discord는 기본적으로 Webhook 검증을 제공하지 않지만, 추가 보안을 위해 IP 화이트리스트를 구현할 수 있습니다.

```java
@Component
public class DiscordWebhookSecurityFilter implements Filter {
    
    // Discord 서버 IP 범위는 공개되지 않음
    // 필요시 자체 검증 로직 구현
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        
        // 커스텀 헤더로 검증
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        String apiKey = httpRequest.getHeader("X-Api-Key");
        
        if (isValidApiKey(apiKey)) {
            chain.doFilter(request, response);
        } else {
            ((HttpServletResponse) response).setStatus(HttpServletResponse.SC_FORBIDDEN);
        }
    }
    
    private boolean isValidApiKey(String apiKey) {
        // 검증 로직
        return true;
    }
}
```

---

## 10. 고급 활용

### 10.1 이미지/파일 첨부

#### 이미지 URL 사용

```java
public void sendImageMessage(String title, String imageUrl) {
    Embed embed = Embed.builder()
        .title(title)
        .image(Image.builder()
            .url(imageUrl)
            .build())
        .color(3447003)
        .build();
    
    sendEmbed(embed);
}
```

#### 썸네일 추가

```java
public void sendWithThumbnail(String title, String thumbnailUrl) {
    Embed embed = Embed.builder()
        .title(title)
        .thumbnail(Thumbnail.builder()
            .url(thumbnailUrl)
            .build())
        .color(3447003)
        .build();
    
    sendEmbed(embed);
}
```

#### 파일 업로드 (Multipart Form Data)

```java
public void sendFileMessage(String content, File file) {
    String url = webhookUrl;
    
    MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
    body.add("content", content);
    body.add("file", new FileSystemResource(file));
    
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.MULTIPART_FORM_DATA);
    
    HttpEntity<MultiValueMap<String, Object>> requestEntity = 
        new HttpEntity<>(body, headers);
    
    restTemplate.postForEntity(url, requestEntity, String.class);
}
```

### 10.2 실전 예제: DailyFeed 통합

#### 시스템 상태 대시보드

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class SystemHealthReporter {
    
    private final DiscordWebhookService discordService;
    
    @Scheduled(cron = "0 0 9,18 * * *") // 오전 9시, 오후 6시
    public void sendHealthReport() {
        SystemMetrics metrics = collectMetrics();
        
        List<Field> fields = List.of(
            Field.builder()
                .name("🖥️ 시스템 리소스")
                .value(String.format(
                    "```\nCPU: %s%%\n메모리: %s / %s\n디스크: %s / %s\n```",
                    metrics.getCpuUsage(),
                    metrics.getUsedMemory(), metrics.getTotalMemory(),
                    metrics.getUsedDisk(), metrics.getTotalDisk()
                ))
                .inline(false)
                .build(),
            Field.builder()
                .name("🔧 서비스 상태")
                .value(formatServiceStatus(metrics))
                .inline(false)
                .build(),
            Field.builder()
                .name("👥 사용자 메트릭스")
                .value(String.format(
                    "```\n활성 사용자: %,d\n신규 가입: %,d\n일일 활동: %,d\n```",
                    metrics.getActiveUsers(),
                    metrics.getNewSignups(),
                    metrics.getDailyActivity()
                ))
                .inline(false)
                .build(),
            Field.builder()
                .name("📊 API 메트릭스")
                .value(String.format(
                    "```\n총 요청: %,d\n성공률: %.2f%%\n평균 응답: %dms\n```",
                    metrics.getTotalRequests(),
                    metrics.getSuccessRate(),
                    metrics.getAvgResponseTime()
                ))
                .inline(false)
                .build()
        );
        
        Embed embed = Embed.builder()
            .title("📊 DailyFeed 시스템 상태 보고")
            .description("현재 시스템 상태 및 주요 메트릭스입니다.")
            .color(3447003) // 파란색
            .fields(fields)
            .timestamp(getCurrentIsoTimestamp())
            .footer(Footer.builder()
                .text("DailyFeed Monitoring System")
                .iconUrl("https://dailyfeed.com/icon.png")
                .build())
            .build();
        
        discordService.sendEmbed(embed);
    }
    
    private String formatServiceStatus(SystemMetrics metrics) {
        return String.format(
            "```\n" +
            "Member:   %s\n" +
            "Content:  %s\n" +
            "Timeline: %s\n" +
            "Activity: %s\n" +
            "Image:    %s\n" +
            "Search:   %s\n" +
            "```",
            getStatusIcon(metrics.getMemberServiceStatus()),
            getStatusIcon(metrics.getContentServiceStatus()),
            getStatusIcon(metrics.getTimelineServiceStatus()),
            getStatusIcon(metrics.getActivityServiceStatus()),
            getStatusIcon(metrics.getImageServiceStatus()),
            getStatusIcon(metrics.getSearchServiceStatus())
        );
    }
    
    private String getStatusIcon(String status) {
        return switch (status) {
            case "UP" -> "🟢 정상";
            case "DOWN" -> "🔴 중단";
            case "DEGRADED" -> "🟡 저하";
            default -> "⚪ 알 수 없음";
        };
    }
}
```

#### 에러 알림 with Stack Trace

```java
@Component
@Aspect
@RequiredArgsConstructor
@Slf4j
public class ErrorNotificationAspect {
    
    private final DiscordWebhookService discordService;
    
    @AfterThrowing(
        pointcut = "execution(* com.dailyfeed..*Service.*(..))",
        throwing = "ex"
    )
    public void notifyError(JoinPoint joinPoint, Exception ex) {
        String className = joinPoint.getSignature().getDeclaringTypeName();
        String methodName = joinPoint.getSignature().getName();
        String errorMessage = ex.getMessage();
        String stackTrace = getStackTrace(ex, 10); // 상위 10줄
        
        List<Field> fields = List.of(
            Field.builder()
                .name("Class")
                .value("`" + className + "`")
                .inline(true)
                .build(),
            Field.builder()
                .name("Method")
                .value("`" + methodName + "`")
                .inline(true)
                .build(),
            Field.builder()
                .name("Error Type")
                .value("`" + ex.getClass().getSimpleName() + "`")
                .inline(true)
                .build(),
            Field.builder()
                .name("Error Message")
                .value("```\n" + errorMessage + "\n```")
                .inline(false)
                .build(),
            Field.builder()
                .name("Stack Trace (Top 10)")
                .value("```java\n" + stackTrace + "\n```")
                .inline(false)
                .build()
        );
        
        Embed embed = Embed.builder()
            .title("🚨 시스템 에러 발생")
            .description("DailyFeed 서비스에서 예외가 발생했습니다.")
            .color(15158332) // 빨간색
            .fields(fields)
            .timestamp(getCurrentIsoTimestamp())
            .footer(Footer.builder()
                .text("DailyFeed Error Monitoring")
                .build())
            .build();
        
        discordService.sendEmbed(embed);
    }
    
    private String getStackTrace(Exception ex, int lines) {
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        ex.printStackTrace(pw);
        
        String fullStackTrace = sw.toString();
        String[] stackLines = fullStackTrace.split("\n");
        
        int lineCount = Math.min(lines, stackLines.length);
        return String.join("\n", Arrays.copyOfRange(stackLines, 0, lineCount));
    }
}
```

#### 배포 진행 상황 알림

```java
@Service
@RequiredArgsConstructor
public class DeploymentNotifier {
    
    private final DiscordWebhookService discordService;
    
    public void notifyDeploymentProgress(DeploymentEvent event) {
        String emoji = switch (event.getStatus()) {
            case STARTED -> "🚀";
            case IN_PROGRESS -> "⏳";
            case TESTING -> "🧪";
            case COMPLETED -> "✅";
            case FAILED -> "❌";
            case ROLLED_BACK -> "⏪";
            default -> "ℹ️";
        };
        
        int color = switch (event.getStatus()) {
            case STARTED, IN_PROGRESS, TESTING -> 3447003; // 파란색
            case COMPLETED -> 3066993; // 초록색
            case FAILED -> 15158332; // 빨간색
            case ROLLED_BACK -> 15105570; // 주황색
            default -> 9807270; // 회색
        };
        
        List<Field> fields = List.of(
            Field.builder()
                .name("Service")
                .value(event.getServiceName())
                .inline(true)
                .build(),
            Field.builder()
                .name("Version")
                .value(event.getVersion())
                .inline(true)
                .build(),
            Field.builder()
                .name("Environment")
                .value(event.getEnvironment())
                .inline(true)
                .build(),
            Field.builder()
                .name("Status")
                .value(event.getStatus().toString())
                .inline(true)
                .build(),
            Field.builder()
                .name("Duration")
                .value(formatDuration(event.getDurationMs()))
                .inline(true)
                .build(),
            Field.builder()
                .name("Deployed By")
                .value(event.getDeployedBy())
                .inline(true)
                .build()
        );
        
        if (event.getDetails() != null) {
            fields.add(Field.builder()
                .name("Details")
                .value(event.getDetails())
                .inline(false)
                .build());
        }
        
        Embed embed = Embed.builder()
            .title(emoji + " 배포 " + event.getStatus().getDescription())
            .color(color)
            .fields(fields)
            .timestamp(getCurrentIsoTimestamp())
            .footer(Footer.builder()
                .text("DailyFeed Deployment Pipeline")
                .build())
            .build();
        
        discordService.sendEmbed(embed);
    }
    
    private String formatDuration(long durationMs) {
        long seconds = durationMs / 1000;
        long minutes = seconds / 60;
        long remainingSeconds = seconds % 60;
        
        if (minutes > 0) {
            return String.format("%dm %ds", minutes, remainingSeconds);
        }
        return String.format("%ds", seconds);
    }
}
```

#### 사용자 활동 알림

```java
@Service
@RequiredArgsConstructor
public class UserActivityNotifier {
    
    private final DiscordWebhookService discordService;
    
    public void notifyMilestone(String milestone, int count) {
        Embed embed = Embed.builder()
            .title("🎉 새로운 이정표 달성!")
            .description(String.format(
                "DailyFeed가 %s 달성했습니다!",
                milestone
            ))
            .color(15844367) // 금색
            .fields(List.of(
                Field.builder()
                    .name("달성 수치")
                    .value(String.format("**%,d**", count))
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("카테고리")
                    .value(milestone)
                    .inline(true)
                    .build()
            ))
            .thumbnail(Thumbnail.builder()
                .url("https://dailyfeed.com/images/trophy.png")
                .build())
            .timestamp(getCurrentIsoTimestamp())
            .footer(Footer.builder()
                .text("DailyFeed Achievements")
                .build())
            .build();
        
        discordService.sendEmbed(embed);
    }
    
    public void notifyViralContent(Content content) {
        Embed embed = Embed.builder()
            .title("🔥 바이럴 콘텐츠 발견!")
            .description(content.getTitle())
            .url("https://dailyfeed.com/content/" + content.getId())
            .color(15105570) // 주황색
            .fields(List.of(
                Field.builder()
                    .name("작성자")
                    .value(content.getAuthor())
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("조회수")
                    .value(String.format("%,d", content.getViews()))
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("좋아요")
                    .value(String.format("%,d", content.getLikes()))
                    .inline(true)
                    .build(),
                Field.builder()
                    .name("댓글")
                    .value(String.format("%,d", content.getComments()))
                    .inline(true)
                    .build()
            ))
            .thumbnail(Thumbnail.builder()
                .url(content.getThumbnailUrl())
                .build())
            .timestamp(getCurrentIsoTimestamp())
            .footer(Footer.builder()
                .text("DailyFeed Trending")
                .build())
            .build();
        
        discordService.sendEmbed(embed);
    }
}
```

### 10.3 여러 Webhook 관리

```java
@Service
@Slf4j
public class MultiChannelDiscordService {
    
    private final RestTemplate restTemplate;
    
    @Value("${discord.webhooks.alerts}")
    private String alertsWebhook;
    
    @Value("${discord.webhooks.deployments}")
    private String deploymentsWebhook;
    
    @Value("${discord.webhooks.errors}")
    private String errorsWebhook;
    
    @Value("${discord.webhooks.metrics}")
    private String metricsWebhook;
    
    public void sendToAlerts(Embed embed) {
        send(alertsWebhook, embed);
    }
    
    public void sendToDeployments(Embed embed) {
        send(deploymentsWebhook, embed);
    }
    
    public void sendToErrors(Embed embed) {
        send(errorsWebhook, embed);
    }
    
    public void sendToMetrics(Embed embed) {
        send(metricsWebhook, embed);
    }
    
    private void send(String webhookUrl, Embed embed) {
        DiscordWebhookRequest request = DiscordWebhookRequest.builder()
            .embeds(List.of(embed))
            .build();
        
        // 전송 로직
    }
}
```

---

## 비교: Slack vs Telegram vs Discord

| 기능 | Slack | Telegram | Discord |
|------|-------|----------|---------|
| **Webhook 방식** | Incoming (단방향) | Webhook (양방향) | Incoming (단방향) |
| **HTTPS 요구** | 권장 | 필수 | 권장 |
| **메시지 포맷** | Block Kit | HTML, Markdown | Embed, Markdown |
| **최대 메시지 길이** | 3000자 (Block Kit) | 4096자 | 2000자 (content)<br/>6000자 (embed) |
| **Rate Limit** | 초당 1개 | 분당 30개 | 초당 5개 (webhook) |
| **파일 업로드** | 지원 | 지원 | 지원 |
| **멘션** | @channel, @here | @username | @everyone, @here, @role |
| **비용** | 유료 플랜 있음 | 무료 | 무료 |
| **주 사용층** | 기업, 팀 협업 | 개인, 커뮤니티 | 게이머, 커뮤니티 |

---

## 참고 자료

### Discord 공식 문서

- **Webhook 가이드**: https://discord.com/developers/docs/resources/webhook
- **Embed 객체**: https://discord.com/developers/docs/resources/channel#embed-object
- **Rate Limits**: https://discord.com/developers/docs/topics/rate-limits
- **Markdown**: https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101

### 개발 도구

- **Embed Visualizer**: https://leovoel.github.io/embed-visualizer/
- **Discord Color Picker**: https://www.spycolor.com/
- **Webhook Tester**: https://discohook.org/

### Spring Boot 관련

- **RestTemplate**: https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/client/RestTemplate.html
- **Jackson**: https://github.com/FasterXML/jackson

---

## 문제 해결

### Webhook URL이 작동하지 않음

**체크리스트:**
1. ✅ URL이 정확히 복사되었는지 확인
2. ✅ Webhook이 삭제되지 않았는지 확인
3. ✅ JSON 형식이 올바른지 확인
4. ✅ 네트워크 연결 확인

```bash
# cURL로 직접 테스트
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"content":"테스트"}' \
  YOUR_WEBHOOK_URL
```

### 400 Bad Request 에러

**원인:**
- 잘못된 JSON 형식
- 필수 필드 누락
- 문자 수 제한 초과
- 잘못된 색상 값

**해결:**
- JSON validator 사용
- 메시지 길이 확인
- 색상은 Decimal 값 사용

### 429 Too Many Requests

**원인:**
- Rate limit 초과

**해결:**
- 메시지 전송 속도 제한
- Retry-After 헤더 확인
- Exponential backoff 구현

### Embed가 표시되지 않음

**체크리스트:**
1. ✅ `embeds` 배열 사용
2. ✅ 필수 필드 확인 (title 또는 description)
3. ✅ 색상 값이 Decimal인지 확인
4. ✅ 전체 크기가 6000자 이하인지 확인

---

## 마무리

이 가이드를 통해 Discord Webhook을 생성하고 Spring Boot 애플리케이션과 연동하여 강력한 알림 시스템을 구축할 수 있습니다.

### 핵심 요약

1. ✅ Discord 서버 및 채널 생성
2. ✅ Webhook 생성 및 URL 복사
3. ✅ Spring Boot에서 RestTemplate로 메시지 전송
4. ✅ Embed로 풍부한 메시지 포맷 활용
5. ✅ Rate Limiting 및 에러 처리 구현
6. ✅ 여러 채널/Webhook 관리

### 추천 사항

- **개발 환경**: 테스트용 서버/채널 분리
- **프로덕션**: 알림 중요도별 채널 분리 (에러, 배포, 메트릭)
- **보안**: Webhook URL을 Secret으로 관리
- **모니터링**: Rate limit 모니터링 및 재시도 로직 구현
- **포맷팅**: Embed 사용으로 시각적 가독성 향상

Discord는 무료이면서도 강력한 Webhook 기능을 제공하므로, 특히 개발팀이나 커뮤니티 중심의 프로젝트에 적합합니다!

---

**작성일:** 2025-01-04  
**버전:** 1.0  
**작성자:** Claude (Anthropic)  
**대상:** DailyFeed Microservices Architecture
