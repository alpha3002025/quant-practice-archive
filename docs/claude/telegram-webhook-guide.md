# 텔레그램 봇 생성 및 Webhook 설정 가이드

텔레그램 봇을 생성하고 Webhook을 설정하여 Spring Boot 애플리케이션과 연동하는 전체 과정을 단계별로 안내합니다.

---

## 목차

1. [텔레그램 가입](#1-텔레그램-가입)
2. [BotFather를 통한 봇 생성](#2-botfather를-통한-봇-생성)
3. [Bot Token 받기](#3-bot-token-받기)
4. [Webhook vs Long Polling](#4-webhook-vs-long-polling)
5. [Webhook 설정](#5-webhook-설정)
6. [Spring Boot 연동](#6-spring-boot-연동)
7. [메시지 수신 및 전송](#7-메시지-수신-및-전송)
8. [주요 주의사항](#8-주요-주의사항)
9. [고급 활용](#9-고급-활용)

---

## 1. 텔레그램 가입

### 텔레그램 설치

**모바일 앱**
- iOS: App Store에서 "Telegram" 검색 및 설치
- Android: Google Play에서 "Telegram" 검색 및 설치

**데스크톱**
- Windows/Mac/Linux: https://desktop.telegram.org
- 웹 버전: https://web.telegram.org

### 계정 생성

1. **전화번호 인증**
   - 텔레그램 앱 실행
   - 전화번호 입력 (국가 코드 포함, 예: +82 10-1234-5678)
   - SMS로 받은 인증 코드 입력

2. **프로필 설정**
   - 이름 입력
   - 프로필 사진 설정 (선택사항)

---

## 2. BotFather를 통한 봇 생성

텔레그램 봇은 공식 봇인 **BotFather**를 통해 생성합니다.

### BotFather 찾기

1. **검색**
   - 텔레그램 검색창에서 `@BotFather` 검색
   - 파란색 체크마크가 있는 공식 계정 선택
   - 또는 직접 링크: https://t.me/botfather

2. **대화 시작**
   - "START" 버튼 클릭
   - BotFather가 사용 가능한 명령어 목록을 보여줍니다

### 새 봇 생성

**명령어 입력**

```
/newbot
```

**봇 이름 설정**

BotFather가 요청하는 정보를 순서대로 입력:

1. **Display Name (표시 이름)**
   ```
   DailyFeed Notification Bot
   ```
   - 사용자에게 보이는 봇의 이름
   - 공백, 특수문자 사용 가능
   - 나중에 변경 가능

2. **Username (사용자명)**
   ```
   dailyfeed_notification_bot
   ```
   - 반드시 `bot` 또는 `_bot`으로 끝나야 함
   - 영문 소문자, 숫자, 언더스코어만 사용
   - 고유해야 함 (이미 사용 중인 이름은 불가)
   - 나중에 변경 불가

**성공 메시지**

```
Done! Congratulations on your new bot.
You will find it at t.me/dailyfeed_notification_bot

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

---

## 3. Bot Token 받기

### Token 정보

생성이 완료되면 BotFather가 **Bot Token**을 제공합니다:

```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
```

**Token 형식:**
- `숫자:영문자+숫자 조합`
- 예: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

### Token 관리

**⚠️ 중요: Token은 절대 공개하지 마세요!**

- GitHub, GitLab 등 공개 저장소에 커밋 금지
- 환경변수나 Secret으로 관리
- Token이 노출되면 즉시 재발급

**Token 재발급**

```
/revoke
```
- BotFather에서 봇 선택
- 새 Token 발급

**Token 확인**

나중에 Token을 잊어버린 경우:

```
/mybots
→ 봇 선택
→ API Token
```

---

## 4. Webhook vs Long Polling

텔레그램 봇은 두 가지 방식으로 메시지를 수신합니다.

### Long Polling (기본 방식)

**특징:**
- 봇이 텔레그램 서버에 주기적으로 요청
- 간단한 구현
- 로컬 개발 환경에서 사용 가능
- HTTPS 인증서 불필요

**단점:**
- 실시간성이 떨어짐
- 서버 리소스 소모

**사용 시나리오:**
- 개발/테스트 환경
- 소규모 봇
- 로컬 개발

### Webhook (권장 방식)

**특징:**
- 텔레그램 서버가 봇 서버로 메시지 푸시
- 실시간 처리
- 효율적인 리소스 사용

**요구사항:**
- **HTTPS 필수** (HTTP 불가)
- 공인 SSL/TLS 인증서 필요
- 공개적으로 접근 가능한 도메인/IP

**사용 시나리오:**
- 프로덕션 환경
- 실시간 알림 시스템
- 대규모 봇

---

## 5. Webhook 설정

### 5.1 사전 준비사항

#### HTTPS 엔드포인트 준비

**옵션 1: 클라우드 배포**
- AWS, GCP, Azure 등에 Spring Boot 앱 배포
- Load Balancer에 SSL 인증서 적용
- 도메인: `https://api.dailyfeed.com`

**옵션 2: ngrok (개발/테스트용)**

```bash
# ngrok 설치 (macOS)
brew install ngrok

# ngrok 설치 (Linux)
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin

# Spring Boot 앱 실행 (포트 8080)
./mvnw spring-boot:run

# ngrok으로 터널 생성
ngrok http 8080
```

**ngrok 출력 예시:**

```
Session Status                online
Account                       user@example.com
Forwarding                    https://abc123.ngrok.io -> http://localhost:8080
```

HTTPS URL: `https://abc123.ngrok.io`

**옵션 3: Kubernetes + Ingress**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dailyfeed-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.dailyfeed.com
    secretName: dailyfeed-tls
  rules:
  - host: api.dailyfeed.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: telegram-webhook-service
            port:
              number: 8080
```

### 5.2 Webhook URL 설정

#### API 호출 방식

**기본 형식:**

```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=<WEBHOOK_URL>
```

**예시:**

```bash
curl -X POST "https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrsTUVwxyz/setWebhook?url=https://api.dailyfeed.com/webhook/telegram"
```

**성공 응답:**

```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

#### Webhook URL 규칙

- **HTTPS 필수**
- 포트: 443, 80, 88, 8443만 허용
- 경로는 자유롭게 설정 가능
  - `/webhook/telegram`
  - `/api/v1/telegram/webhook`
  - `/bot/updates`

**잘못된 예시:**

```bash
# ❌ HTTP 사용 불가
url=http://api.dailyfeed.com/webhook

# ❌ 지원하지 않는 포트
url=https://api.dailyfeed.com:8080/webhook

# ✅ 올바른 예시
url=https://api.dailyfeed.com/webhook/telegram
url=https://api.dailyfeed.com:8443/webhook/telegram
```

### 5.3 Webhook 상태 확인

```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

**응답 예시:**

```json
{
  "ok": true,
  "result": {
    "url": "https://api.dailyfeed.com/webhook/telegram",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "max_connections": 40,
    "ip_address": "203.0.113.1"
  }
}
```

**주요 필드:**
- `url`: 설정된 Webhook URL
- `pending_update_count`: 대기 중인 업데이트 수 (0이 정상)
- `last_error_date`: 마지막 에러 발생 시간
- `last_error_message`: 에러 메시지

### 5.4 Webhook 삭제

Long Polling으로 전환하거나 Webhook을 제거할 때:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

---

## 6. Spring Boot 연동

### 6.1 의존성 추가

#### Maven (pom.xml)

```xml
<dependencies>
    <!-- Spring Boot Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- Telegram Bot API (선택사항) -->
    <dependency>
        <groupId>org.telegram</groupId>
        <artifactId>telegrambots</artifactId>
        <version>6.8.0</version>
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
    implementation 'org.telegram:telegrambots:6.8.0'
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
}
```

### 6.2 환경 설정

#### application.yml

```yaml
telegram:
  bot:
    token: ${TELEGRAM_BOT_TOKEN:1234567890:ABCdefGHIjklMNOpqrsTUVwxyz}
    username: ${TELEGRAM_BOT_USERNAME:dailyfeed_notification_bot}
    webhook-url: ${TELEGRAM_WEBHOOK_URL:https://api.dailyfeed.com/webhook/telegram}
  enabled: ${TELEGRAM_ENABLED:true}

server:
  port: 8080
```

#### .env 파일 (로컬 개발)

```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_USERNAME=dailyfeed_notification_bot
TELEGRAM_WEBHOOK_URL=https://abc123.ngrok.io/webhook/telegram
TELEGRAM_ENABLED=true
```

### 6.3 DTO 정의

#### TelegramUpdate.java

```java
package com.dailyfeed.common.telegram.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class TelegramUpdate {
    
    @JsonProperty("update_id")
    private Long updateId;
    
    private Message message;
    
    @JsonProperty("edited_message")
    private Message editedMessage;
    
    @JsonProperty("callback_query")
    private CallbackQuery callbackQuery;
    
    @Data
    public static class Message {
        @JsonProperty("message_id")
        private Long messageId;
        
        private User from;
        private Chat chat;
        private Long date;
        private String text;
        
        @JsonProperty("reply_to_message")
        private Message replyToMessage;
    }
    
    @Data
    public static class User {
        private Long id;
        
        @JsonProperty("is_bot")
        private Boolean isBot;
        
        @JsonProperty("first_name")
        private String firstName;
        
        @JsonProperty("last_name")
        private String lastName;
        
        private String username;
        
        @JsonProperty("language_code")
        private String languageCode;
    }
    
    @Data
    public static class Chat {
        private Long id;
        private String type;  // "private", "group", "supergroup", "channel"
        private String title;
        private String username;
        
        @JsonProperty("first_name")
        private String firstName;
        
        @JsonProperty("last_name")
        private String lastName;
    }
    
    @Data
    public static class CallbackQuery {
        private String id;
        private User from;
        private Message message;
        private String data;
    }
}
```

#### SendMessageRequest.java

```java
package com.dailyfeed.common.telegram.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class SendMessageRequest {
    
    @JsonProperty("chat_id")
    private Long chatId;
    
    private String text;
    
    @JsonProperty("parse_mode")
    private String parseMode;  // "Markdown", "MarkdownV2", "HTML"
    
    @JsonProperty("disable_web_page_preview")
    private Boolean disableWebPagePreview;
    
    @JsonProperty("disable_notification")
    private Boolean disableNotification;
    
    @JsonProperty("reply_to_message_id")
    private Long replyToMessageId;
    
    @JsonProperty("reply_markup")
    private Object replyMarkup;  // InlineKeyboardMarkup, ReplyKeyboardMarkup 등
}
```

### 6.4 Webhook Controller

```java
package com.dailyfeed.common.telegram.controller;

import com.dailyfeed.common.telegram.dto.TelegramUpdate;
import com.dailyfeed.common.telegram.service.TelegramWebhookService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/webhook/telegram")
@RequiredArgsConstructor
@Slf4j
public class TelegramWebhookController {
    
    private final TelegramWebhookService webhookService;
    
    @PostMapping
    public ResponseEntity<Void> handleWebhook(@RequestBody TelegramUpdate update) {
        log.info("텔레그램 Webhook 수신: updateId={}", update.getUpdateId());
        
        try {
            webhookService.processUpdate(update);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            log.error("Webhook 처리 중 에러 발생", e);
            // 텔레그램은 200 OK를 기대하므로 에러가 발생해도 200 반환
            return ResponseEntity.ok().build();
        }
    }
    
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("OK");
    }
}
```

### 6.5 Webhook Service

```java
package com.dailyfeed.common.telegram.service;

import com.dailyfeed.common.telegram.dto.TelegramUpdate;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class TelegramWebhookService {
    
    private final TelegramMessageService messageService;
    
    public void processUpdate(TelegramUpdate update) {
        if (update.getMessage() != null) {
            handleMessage(update.getMessage());
        } else if (update.getEditedMessage() != null) {
            handleEditedMessage(update.getEditedMessage());
        } else if (update.getCallbackQuery() != null) {
            handleCallbackQuery(update.getCallbackQuery());
        }
    }
    
    private void handleMessage(TelegramUpdate.Message message) {
        Long chatId = message.getChat().getId();
        String text = message.getText();
        
        log.info("메시지 수신 - chatId: {}, text: {}", chatId, text);
        
        // 명령어 처리
        if (text != null && text.startsWith("/")) {
            handleCommand(chatId, text);
            return;
        }
        
        // 일반 메시지 처리
        handleTextMessage(chatId, text);
    }
    
    private void handleCommand(Long chatId, String command) {
        switch (command.split(" ")[0]) {
            case "/start":
                messageService.sendMessage(chatId, 
                    "안녕하세요! DailyFeed 알림 봇입니다.\n\n" +
                    "사용 가능한 명령어:\n" +
                    "/status - 시스템 상태 확인\n" +
                    "/subscribe - 알림 구독\n" +
                    "/unsubscribe - 알림 구독 해제\n" +
                    "/help - 도움말"
                );
                break;
                
            case "/status":
                messageService.sendMessage(chatId, "✅ 모든 시스템이 정상 작동 중입니다.");
                break;
                
            case "/help":
                messageService.sendMessage(chatId, "도움이 필요하신가요? support@dailyfeed.com으로 문의해주세요.");
                break;
                
            default:
                messageService.sendMessage(chatId, "알 수 없는 명령어입니다. /help를 입력해보세요.");
        }
    }
    
    private void handleTextMessage(Long chatId, String text) {
        // 일반 텍스트 메시지 처리 로직
        log.info("일반 메시지 처리: {}", text);
    }
    
    private void handleEditedMessage(TelegramUpdate.Message message) {
        log.info("수정된 메시지: {}", message.getText());
    }
    
    private void handleCallbackQuery(TelegramUpdate.CallbackQuery query) {
        log.info("콜백 쿼리: {}", query.getData());
        // 인라인 버튼 클릭 처리
    }
}
```

### 6.6 Message Service

```java
package com.dailyfeed.common.telegram.service;

import com.dailyfeed.common.telegram.dto.SendMessageRequest;
import com.fasterxml.jackson.databind.JsonNode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@Slf4j
public class TelegramMessageService {
    
    private final RestTemplate restTemplate;
    private final String botToken;
    private final String apiUrl;
    
    public TelegramMessageService(
            RestTemplate restTemplate,
            @Value("${telegram.bot.token}") String botToken) {
        this.restTemplate = restTemplate;
        this.botToken = botToken;
        this.apiUrl = "https://api.telegram.org/bot" + botToken;
    }
    
    /**
     * 간단한 텍스트 메시지 전송
     */
    public void sendMessage(Long chatId, String text) {
        SendMessageRequest request = SendMessageRequest.builder()
            .chatId(chatId)
            .text(text)
            .build();
        
        sendMessage(request);
    }
    
    /**
     * 메시지 전송 (전체 옵션)
     */
    public void sendMessage(SendMessageRequest request) {
        try {
            String url = apiUrl + "/sendMessage";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<SendMessageRequest> entity = new HttpEntity<>(request, headers);
            
            ResponseEntity<JsonNode> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                JsonNode.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                log.info("메시지 전송 성공: chatId={}", request.getChatId());
            }
        } catch (Exception e) {
            log.error("메시지 전송 실패: chatId={}", request.getChatId(), e);
        }
    }
    
    /**
     * Markdown 형식 메시지 전송
     */
    public void sendMarkdownMessage(Long chatId, String markdown) {
        SendMessageRequest request = SendMessageRequest.builder()
            .chatId(chatId)
            .text(markdown)
            .parseMode("MarkdownV2")
            .build();
        
        sendMessage(request);
    }
    
    /**
     * HTML 형식 메시지 전송
     */
    public void sendHtmlMessage(Long chatId, String html) {
        SendMessageRequest request = SendMessageRequest.builder()
            .chatId(chatId)
            .text(html)
            .parseMode("HTML")
            .build();
        
        sendMessage(request);
    }
    
    /**
     * 에러 알림 전송
     */
    public void sendErrorAlert(Long chatId, String serviceName, String errorMessage) {
        String message = String.format(
            "🚨 <b>시스템 에러 발생</b>\n\n" +
            "<b>Service:</b> %s\n" +
            "<b>Error:</b> <code>%s</code>",
            serviceName,
            errorMessage
        );
        
        sendHtmlMessage(chatId, message);
    }
    
    /**
     * 인라인 키보드와 함께 메시지 전송
     */
    public void sendMessageWithButtons(Long chatId, String text, List<List<Map<String, String>>> buttons) {
        Map<String, Object> inlineKeyboard = new HashMap<>();
        inlineKeyboard.put("inline_keyboard", buttons);
        
        SendMessageRequest request = SendMessageRequest.builder()
            .chatId(chatId)
            .text(text)
            .replyMarkup(inlineKeyboard)
            .build();
        
        sendMessage(request);
    }
}
```

---

## 7. 메시지 수신 및 전송

### 7.1 메시지 수신 흐름

```
사용자 → 텔레그램 서버 → Webhook URL → Spring Boot Controller → Service → 처리
```

### 7.2 메시지 전송 예제

#### 간단한 알림

```java
@Service
@RequiredArgsConstructor
public class NotificationService {
    
    private final TelegramMessageService telegramService;
    
    @Value("${telegram.admin.chat-id}")
    private Long adminChatId;
    
    public void notifyNewUser(String email) {
        telegramService.sendMessage(
            adminChatId,
            "✅ 새 회원 가입: " + email
        );
    }
    
    public void notifyError(String service, String error) {
        telegramService.sendErrorAlert(
            adminChatId,
            service,
            error
        );
    }
}
```

#### 포맷팅된 메시지

```java
// HTML 형식
String html = """
    <b>DailyFeed 시스템 상태</b>
    
    <b>CPU:</b> 45%
    <b>메모리:</b> 2.1GB / 4GB
    <b>활성 사용자:</b> 1,234명
    
    <i>마지막 업데이트: 2025-01-04 15:30</i>
    """;

telegramService.sendHtmlMessage(chatId, html);

// Markdown 형식 (MarkdownV2)
String markdown = """
    *DailyFeed 시스템 상태*
    
    *CPU:* 45%
    *메모리:* 2\\.1GB / 4GB
    *활성 사용자:* 1,234명
    
    _마지막 업데이트: 2025\\-01\\-04 15:30_
    """;

telegramService.sendMarkdownMessage(chatId, markdown);
```

#### 인라인 버튼과 함께

```java
public void sendApprovalRequest(Long chatId, String requestId) {
    List<List<Map<String, String>>> buttons = List.of(
        List.of(
            Map.of(
                "text", "✅ 승인",
                "callback_data", "approve_" + requestId
            ),
            Map.of(
                "text", "❌ 거부",
                "callback_data", "reject_" + requestId
            )
        ),
        List.of(
            Map.of(
                "text", "📄 자세히 보기",
                "url", "https://dailyfeed.com/requests/" + requestId
            )
        )
    );
    
    telegramService.sendMessageWithButtons(
        chatId,
        "새로운 승인 요청이 있습니다.",
        buttons
    );
}
```

### 7.3 Chat ID 얻기

사용자의 Chat ID를 얻는 방법:

**방법 1: 봇에게 메시지 보내기**

1. 사용자가 봇에게 `/start` 메시지 전송
2. Webhook에서 `message.chat.id` 확인
3. 로그나 데이터베이스에 저장

```java
private void handleCommand(Long chatId, String command) {
    if (command.equals("/start")) {
        log.info("새 사용자 Chat ID: {}", chatId);
        // DB에 저장
        userRepository.saveChatId(chatId);
    }
}
```

**방법 2: getUpdates API 사용 (개발용)**

```bash
curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
```

응답에서 `message.chat.id` 확인

---

## 8. 주요 주의사항

### 8.1 보안

#### Token 관리

```bash
# ❌ 절대 금지
git add application.yml  # Token 포함된 파일
git commit -m "Add config"

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
  name: telegram-bot-secret
  namespace: dailyfeed
type: Opaque
stringData:
  bot-token: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
  admin-chat-id: "123456789"
```

```yaml
# Deployment
env:
- name: TELEGRAM_BOT_TOKEN
  valueFrom:
    secretKeyRef:
      name: telegram-bot-secret
      key: bot-token
```

### 8.2 Rate Limiting

**텔레그램 API 제한:**
- 그룹당 초당 20개 메시지
- 전체: 분당 30개 메시지
- 같은 채팅방: 초당 1개 메시지

**429 Error 처리:**

```java
public void sendMessageWithRetry(Long chatId, String text) {
    int maxRetries = 3;
    int retryDelay = 1000; // 1초
    
    for (int i = 0; i < maxRetries; i++) {
        try {
            sendMessage(chatId, text);
            return;
        } catch (HttpClientErrorException e) {
            if (e.getStatusCode() == HttpStatus.TOO_MANY_REQUESTS) {
                log.warn("Rate limit 초과, {}ms 후 재시도", retryDelay);
                Thread.sleep(retryDelay);
                retryDelay *= 2; // Exponential backoff
            } else {
                throw e;
            }
        }
    }
}
```

### 8.3 Webhook 검증

**IP 화이트리스트 (선택사항):**

텔레그램 서버 IP 대역:
- 149.154.160.0/20
- 91.108.4.0/22

```java
@Component
public class TelegramWebhookFilter implements Filter {
    
    private static final List<String> ALLOWED_IP_RANGES = List.of(
        "149.154.160.0/20",
        "91.108.4.0/22"
    );
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        
        String remoteAddr = request.getRemoteAddr();
        
        if (isAllowedIP(remoteAddr)) {
            chain.doFilter(request, response);
        } else {
            log.warn("허용되지 않은 IP에서 접근 시도: {}", remoteAddr);
            ((HttpServletResponse) response).setStatus(HttpServletResponse.SC_FORBIDDEN);
        }
    }
    
    private boolean isAllowedIP(String ip) {
        // IP 범위 검증 로직
        return true; // 간단한 예제
    }
}
```

### 8.4 메시지 포맷 주의사항

**MarkdownV2 이스케이프:**

다음 문자는 이스케이프 필요:
```
_ * [ ] ( ) ~ ` > # + - = | { } . !
```

```java
public String escapeMarkdownV2(String text) {
    return text.replaceAll("([_*\\[\\]()~`>#+=|{}.!-])", "\\\\$1");
}
```

**HTML 태그:**

지원되는 태그:
- `<b>굵게</b>`
- `<i>기울임</i>`
- `<u>밑줄</u>`
- `<s>취소선</s>`
- `<code>코드</code>`
- `<pre>코드블록</pre>`
- `<a href="URL">링크</a>`

---

## 9. 고급 활용

### 9.1 파일 전송

```java
public void sendPhoto(Long chatId, String photoUrl, String caption) {
    String url = apiUrl + "/sendPhoto";
    
    Map<String, Object> request = Map.of(
        "chat_id", chatId,
        "photo", photoUrl,
        "caption", caption
    );
    
    // API 호출
}

public void sendDocument(Long chatId, String documentUrl, String caption) {
    String url = apiUrl + "/sendDocument";
    
    Map<String, Object> request = Map.of(
        "chat_id", chatId,
        "document", documentUrl,
        "caption", caption
    );
    
    // API 호출
}
```

### 9.2 그룹/채널 관리

**봇을 그룹에 추가:**

1. 그룹 생성
2. 그룹에 봇 추가 (`@your_bot_username`)
3. 봇에게 관리자 권한 부여 (선택)

**채널에 메시지 전송:**

```java
// 채널 ID는 @채널명 또는 -100으로 시작하는 숫자
Long channelId = -1001234567890L;
telegramService.sendMessage(channelId, "공지사항입니다.");
```

### 9.3 커스텀 키보드

```java
public void sendReplyKeyboard(Long chatId) {
    Map<String, Object> keyboard = Map.of(
        "keyboard", List.of(
            List.of(
                Map.of("text", "🏠 홈"),
                Map.of("text", "📊 통계")
            ),
            List.of(
                Map.of("text", "⚙️ 설정"),
                Map.of("text", "❓ 도움말")
            )
        ),
        "resize_keyboard", true,
        "one_time_keyboard", false
    );
    
    SendMessageRequest request = SendMessageRequest.builder()
        .chatId(chatId)
        .text("메뉴를 선택하세요:")
        .replyMarkup(keyboard)
        .build();
    
    sendMessage(request);
}
```

### 9.4 Webhook 초기화 자동화

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class TelegramWebhookInitializer implements ApplicationListener<ContextRefreshedEvent> {
    
    @Value("${telegram.bot.token}")
    private String botToken;
    
    @Value("${telegram.bot.webhook-url}")
    private String webhookUrl;
    
    @Value("${telegram.enabled}")
    private boolean enabled;
    
    private final RestTemplate restTemplate;
    
    @Override
    public void onApplicationEvent(ContextRefreshedEvent event) {
        if (!enabled) {
            log.info("텔레그램 봇이 비활성화되어 있습니다.");
            return;
        }
        
        try {
            setWebhook();
            log.info("텔레그램 Webhook 설정 완료: {}", webhookUrl);
        } catch (Exception e) {
            log.error("텔레그램 Webhook 설정 실패", e);
        }
    }
    
    private void setWebhook() {
        String url = String.format(
            "https://api.telegram.org/bot%s/setWebhook?url=%s",
            botToken,
            webhookUrl
        );
        
        ResponseEntity<JsonNode> response = restTemplate.getForEntity(url, JsonNode.class);
        
        if (response.getStatusCode() == HttpStatus.OK) {
            JsonNode body = response.getBody();
            if (body != null && body.get("ok").asBoolean()) {
                log.info("Webhook 설정 성공");
            } else {
                log.error("Webhook 설정 실패: {}", body);
            }
        }
    }
}
```

### 9.5 에러 모니터링 통합

```java
@Component
@Aspect
@RequiredArgsConstructor
@Slf4j
public class ErrorNotificationAspect {
    
    private final TelegramMessageService telegramService;
    
    @Value("${telegram.admin.chat-id}")
    private Long adminChatId;
    
    @AfterThrowing(
        pointcut = "execution(* com.dailyfeed..*Service.*(..))",
        throwing = "ex"
    )
    public void notifyError(JoinPoint joinPoint, Exception ex) {
        String serviceName = joinPoint.getSignature().getDeclaringTypeName();
        String methodName = joinPoint.getSignature().getName();
        String errorMessage = ex.getMessage();
        
        String message = String.format(
            "🚨 <b>에러 발생</b>\n\n" +
            "<b>Service:</b> %s\n" +
            "<b>Method:</b> %s\n" +
            "<b>Error:</b> <code>%s</code>",
            serviceName,
            methodName,
            errorMessage
        );
        
        telegramService.sendHtmlMessage(adminChatId, message);
    }
}
```

---

## 10. 실전 예제: DailyFeed 통합

### 10.1 시스템 상태 알림

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class SystemHealthNotifier {
    
    private final TelegramMessageService telegramService;
    
    @Value("${telegram.admin.chat-id}")
    private Long adminChatId;
    
    @Scheduled(cron = "0 0 9 * * *") // 매일 오전 9시
    public void sendDailyHealthReport() {
        SystemMetrics metrics = collectMetrics();
        
        String report = String.format("""
            📊 <b>DailyFeed 일일 상태 보고</b>
            
            <b>시스템 메트릭스</b>
            • CPU 사용률: %s%%
            • 메모리: %s / %s
            • 디스크: %s / %s
            
            <b>서비스 상태</b>
            • Member Service: %s
            • Content Service: %s
            • Timeline Service: %s
            • Activity Service: %s
            • Image Service: %s
            • Search Service: %s
            
            <b>비즈니스 메트릭스</b>
            • 활성 사용자: %,d명
            • 신규 가입: %,d명
            • 생성된 콘텐츠: %,d개
            • API 요청: %,d회
            
            <i>보고 시간: %s</i>
            """,
            metrics.getCpuUsage(),
            metrics.getUsedMemory(), metrics.getTotalMemory(),
            metrics.getUsedDisk(), metrics.getTotalDisk(),
            getStatusEmoji(metrics.getMemberServiceStatus()),
            getStatusEmoji(metrics.getContentServiceStatus()),
            getStatusEmoji(metrics.getTimelineServiceStatus()),
            getStatusEmoji(metrics.getActivityServiceStatus()),
            getStatusEmoji(metrics.getImageServiceStatus()),
            getStatusEmoji(metrics.getSearchServiceStatus()),
            metrics.getActiveUsers(),
            metrics.getNewSignups(),
            metrics.getCreatedContents(),
            metrics.getApiRequests(),
            LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
        );
        
        telegramService.sendHtmlMessage(adminChatId, report);
    }
    
    private String getStatusEmoji(String status) {
        return switch (status) {
            case "UP" -> "🟢 정상";
            case "DOWN" -> "🔴 중단";
            case "DEGRADED" -> "🟡 저하";
            default -> "⚪ 알 수 없음";
        };
    }
    
    private SystemMetrics collectMetrics() {
        // 실제 메트릭 수집 로직
        return new SystemMetrics();
    }
}
```

### 10.2 배포 알림

```java
@Service
@RequiredArgsConstructor
public class DeploymentNotifier {
    
    private final TelegramMessageService telegramService;
    
    @Value("${telegram.admin.chat-id}")
    private Long adminChatId;
    
    public void notifyDeploymentStart(String service, String version) {
        String message = String.format(
            "🚀 <b>배포 시작</b>\n\n" +
            "<b>Service:</b> %s\n" +
            "<b>Version:</b> %s\n" +
            "<b>Time:</b> %s",
            service,
            version,
            LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"))
        );
        
        telegramService.sendHtmlMessage(adminChatId, message);
    }
    
    public void notifyDeploymentSuccess(String service, String version, long durationMs) {
        String message = String.format(
            "✅ <b>배포 완료</b>\n\n" +
            "<b>Service:</b> %s\n" +
            "<b>Version:</b> %s\n" +
            "<b>Duration:</b> %d초\n" +
            "<b>Status:</b> 성공",
            service,
            version,
            durationMs / 1000
        );
        
        telegramService.sendHtmlMessage(adminChatId, message);
    }
    
    public void notifyDeploymentFailure(String service, String version, String error) {
        String message = String.format(
            "❌ <b>배포 실패</b>\n\n" +
            "<b>Service:</b> %s\n" +
            "<b>Version:</b> %s\n" +
            "<b>Error:</b> <code>%s</code>\n\n" +
            "⚠️ 즉시 확인이 필요합니다!",
            service,
            version,
            error
        );
        
        telegramService.sendHtmlMessage(adminChatId, message);
    }
}
```

### 10.3 사용자 인터랙션

```java
@Service
@RequiredArgsConstructor
public class UserNotificationService {
    
    private final TelegramMessageService telegramService;
    private final UserRepository userRepository;
    
    public void notifyNewFollower(Long userId, String followerName) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));
        
        if (user.getTelegramChatId() != null) {
            String message = String.format(
                "👤 %s님이 회원님을 팔로우했습니다!",
                followerName
            );
            
            telegramService.sendMessage(user.getTelegramChatId(), message);
        }
    }
    
    public void notifyNewComment(Long userId, String commenterName, String contentTitle) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));
        
        if (user.getTelegramChatId() != null) {
            String message = String.format(
                "💬 %s님이 \"%s\"에 댓글을 남겼습니다.",
                commenterName,
                contentTitle
            );
            
            telegramService.sendMessage(user.getTelegramChatId(), message);
        }
    }
}
```

---

## 참고 자료

### 텔레그램 공식 문서

- **Bot API**: https://core.telegram.org/bots/api
- **봇 소개**: https://core.telegram.org/bots
- **Webhook 가이드**: https://core.telegram.org/bots/webhooks
- **Formatting Options**: https://core.telegram.org/bots/api#formatting-options

### 개발 도구

- **Bot API Tester**: https://t.me/BotFather
- **ngrok**: https://ngrok.com
- **Postman Collection**: https://www.postman.com/telegram

### Spring Boot 관련

- **Telegram Bots Library**: https://github.com/rubenlagus/TelegramBots
- **RestTemplate**: https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/client/RestTemplate.html

---

## 문제 해결

### Webhook이 호출되지 않음

**체크리스트:**
1. ✅ HTTPS 사용 확인
2. ✅ 지원되는 포트 사용 (443, 80, 88, 8443)
3. ✅ SSL 인증서 유효성 확인
4. ✅ 방화벽에서 텔레그램 IP 허용
5. ✅ `getWebhookInfo`로 상태 확인

```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

### "Bad Request: wrong webhook url" 에러

**원인:**
- HTTP 사용 (HTTPS 필수)
- 지원하지 않는 포트
- 잘못된 URL 형식

**해결:**
```bash
# ❌ 잘못된 예
https://example.com:8080/webhook

# ✅ 올바른 예
https://example.com/webhook
https://example.com:8443/webhook
```

### 메시지 전송 실패

**400 Bad Request:**
- JSON 형식 오류
- 필수 필드 누락 (chat_id, text)
- 잘못된 parse_mode

**403 Forbidden:**
- 봇이 차단됨
- 그룹에서 봇이 제거됨

**429 Too Many Requests:**
- Rate limit 초과
- Exponential backoff 적용

---

## 마무리

이 가이드를 통해 텔레그램 봇을 생성하고 Spring Boot 애플리케이션과 Webhook으로 연동하여 실시간 알림 시스템을 구축할 수 있습니다.

### 핵심 요약

1. ✅ BotFather로 봇 생성 및 Token 발급
2. ✅ HTTPS 엔드포인트 준비 (ngrok, 클라우드, Kubernetes)
3. ✅ Webhook URL 설정 (`setWebhook` API)
4. ✅ Spring Boot Controller로 메시지 수신
5. ✅ Telegram API로 메시지 전송
6. ✅ Rate Limiting 및 에러 처리

### Slack vs Telegram 비교

| 기능 | Slack | Telegram |
|------|-------|----------|
| **Webhook 방식** | Incoming Webhook (단방향) | Webhook (양방향) + Long Polling |
| **HTTPS 요구사항** | 권장 | 필수 |
| **메시지 포맷** | Block Kit, Attachments | HTML, Markdown, MarkdownV2 |
| **Rate Limit** | 초당 1개 | 분당 30개 (그룹 초당 20개) |
| **사용자 ID** | Workspace 기반 | 전역 Chat ID |
| **비용** | 유료 플랜 있음 | 무료 |

### 추천 사항

- 개발 환경: ngrok으로 빠른 테스트
- 프로덕션: Kubernetes + Ingress + Let's Encrypt
- 모니터링: Webhook 상태를 주기적으로 확인
- 에러 처리: 모든 API 호출에 try-catch 적용
- 보안: Token을 Secret으로 관리

---

**작성일:** 2025-01-04  
**버전:** 1.0  
**작성자:** Claude (Anthropic)  
**대상:** DailyFeed Microservices Architecture
