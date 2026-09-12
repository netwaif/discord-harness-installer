# 브라우저 조작 레시피

chrome-devtools MCP로 Discord 포털·웹을 다룰 때 실제로 통한 스니펫 모음. Discord는 React + 숨은 input + 가상 스크롤이라 표준 클릭이 자주 실패한다. 새로 짜기 전에 여기부터 본다.

## 목차

- [왜 click/fill이 실패하는가](#왜-clickfill이-실패하는가)
- [큰 스냅샷 다루기](#큰-스냅샷-다루기)
- [서버·채널 ID 수집](#서버채널-id-수집)
- [사용자 ID 읽기](#사용자-id-읽기)
- [서버 멤버 목록 읽기](#서버-멤버-목록-읽기)
- [앱 목록 읽기 / 중복 검사](#앱-목록-읽기--중복-검사)
- [앱 생성](#앱-생성)
- [CAPTCHA 대기](#captcha-대기)
- [Intent 켜고 저장·검증](#intent-켜고-저장검증)
- [OAuth2 URL Generator](#oauth2-url-generator)
- [초대 승인 흐름](#초대-승인-흐름)
- [채널 만들기 (비공개)](#채널-만들기-비공개)
- [채널 권한에 봇 추가](#채널-권한에-봇-추가)
- [잘못 넣은 권한 제거](#잘못-넣은-권한-제거)
- [UI 라벨 대응표](#ui-라벨-대응표)

---

## 왜 click/fill이 실패하는가

Discord의 체크박스·스위치는 시각 요소가 `div`이고 실제 `input[type=checkbox]`는 `opacity:0`으로 숨어 있다. `mcp__chrome-devtools__click`과 `fill`은 이 숨은 input을 조작 대상으로 잡고 **"did not become interactive within the configured timeout"**으로 실패한다.

해법은 `evaluate_script`로 **감싸는 `label`을 클릭**하는 것:

```js
() => { const inp = document.querySelector('SELECTOR'); (inp.closest('label') || inp.parentElement).click(); }
```

주의 두 가지:

- 클릭 직후 `inp.checked`를 읽으면 **아직 false로 나올 수 있다**(React가 다음 틱에 반영). 상태 확인은 300~500ms 쉬고 별도 호출로 한다.
- 한 호출에서 여러 개를 연속 토글하면 재렌더로 참조가 어긋나 **일부만 먹는다.** 하나 누를 때마다 짧게 쉬고, 끝나고 전체 상태를 다시 읽어 검증한다.

반대로 **`role="option"`, `role="tab"`, 일반 `button`은 `evaluate_script`의 `.click()`으로 잘 먹는다.** 다이얼로그의 `만들기`처럼 스냅샷 uid가 잡히는 것은 `mcp__chrome-devtools__click`을 써도 된다.

**`label.click()`이 안 먹는 스위치가 있다.** 채널 만들기의 `비공개 채널` 토글이 그렇다(label을 눌러도, 좌표에 합성 포인터 이벤트를 쏴도 안 바뀐다 — 그 지점의 실제 요소가 장식용 `svg`다). 이럴 때는 **숨은 input을 직접** 누른다:

```js
() => { const inp = document.querySelector('[role="dialog"] input[type="checkbox"]'); inp.click(); }
```

순서는 `label.click()` → 상태 확인 → 안 바뀌었으면 `input.click()`. 둘 중 하나는 먹는다.

**상태 판정은 화면으로 한다.** `input.checked`는 React 제어 컴포넌트라 클릭 직후 거짓을 말하는 경우가 있다(실제로 체크됐는데 `false`, 반대도 있음). 공개/비공개처럼 **틀리면 곤란한 값**은 `take_screenshot(pageId, uid: <다이얼로그 uid>)`로 눈으로 확인한다. 버튼 라벨이 바뀌는 것도 좋은 신호다(`채널 만들기` → `다음`).

## 큰 스냅샷 다루기

Discord 웹의 `take_snapshot`은 수만 자라 컨텍스트를 잡아먹는다. **파일로 저장하고 grep한다.**

```
take_snapshot(pageId, filePath: "<작업폴더>/.tmp_snap.txt")
```
→ `grep -nE "권한|멤버 또는 역할 추가|채널 편집" .tmp_snap.txt`

저장 경로는 워크스페이스 루트 안이어야 한다(스크래치패드 경로는 거부된다). **작업이 끝나면 `.tmp_*` 파일을 지운다.**

## 서버·채널 ID 수집

서버 목록(왼쪽 사이드바). `a[href]`가 없고 `data-list-item-id`에 ID가 박혀 있다:

```js
() => Array.from(document.querySelectorAll('[data-list-item-id^="guildsnav"]'))
  .map(e => ({ id: e.getAttribute('data-list-item-id').replace('guildsnav___',''),
               name: e.querySelector('[data-dnd-name]')?.getAttribute('data-dnd-name') || '' }))
```

채널 목록. **채널명은 `innerText`가 아니라 `aria-label`에 있다**(innerText는 "텍스트", "텍스트 (제한)" 같은 유형명이 나온다):

```js
() => Array.from(document.querySelectorAll('a[href^="/channels/<GUILD_ID>/"]'))
  .map(a => ({ id: a.getAttribute('href').split('/')[3],
               label: a.getAttribute('aria-label') }))
```

`label` 예: `"기술검증팀 (채팅 채널), 비공개 채널(잠김)"` — 비공개 여부까지 같이 읽힌다.

## 사용자 ID 읽기

**아바타 이미지 URL의 숫자가 곧 사용자 ID다.** 개발자 모드도, 우클릭도 필요 없다. 채널을 하나 열어 두고(멤버 목록이 보이면 더 잘 잡힌다) 실행한다:

```js
async () => {
  for (let i=0;i<30;i++){ if(document.querySelector('img[src*="cdn.discordapp.com/avatars/"]')) break;
                          await new Promise(r=>setTimeout(r,700)); }
  await new Promise(r=>setTimeout(r,2000));
  const out = Array.from(document.querySelectorAll('img[src*="cdn.discordapp.com/avatars/"]')).map(img=>{
    const m = img.getAttribute('src').match(/avatars\/(\d+)\//);
    let n = img.parentElement, label='';
    for (let i=0;i<6 && n;i++){ const t=(n.innerText||'').trim(); if(t){ label=t.replace(/\n/g,' ').slice(0,40); break; } n=n.parentElement; }
    return { id: m?m[1]:null, label };
  });
  const seen=new Set(); return out.filter(o=>{ const k=o.id+o.label; if(seen.has(k)) return false; seen.add(k); return true; });
}
```

`label`로 누구 것인지 가린다(`"netwaif 서버 주인"`, `"docs-editor 앱"`). 운영자 본인 ID는 `서버 주인` 이 붙은 줄이거나, 좌하단 사용자 패널의 아바타다.

**봇의 사용자 ID는 Application ID와 같다.** 서버의 봇 8개에서 이 방법으로 읽은 ID가 포털의 Application ID와 전부 일치했다 — 봇은 따로 찾을 것 없이 앱 ID를 그대로 쓰면 된다.

**기본 아바타를 쓰는 계정은 이 방법이 안 통한다**(URL이 `embed/avatars/N.png`라 ID가 없다). 그때는 사용자에게 **디스코드 설정 → 고급 → 개발자 모드**를 켜고 이름 우클릭 → `사용자 ID 복사`를 부탁한다.

## 서버 멤버 목록 읽기

멤버 목록이 접혀 있으면 먼저 `멤버 목록 표시하기` 버튼을 누른다(스냅샷에서 uid를 찾아 `click`). 그다음 스냅샷을 파일로 떠서 `멤버 목록` 이후 구간의 `listitem`을 본다:

```
sed -n '/멤버 목록/,$p' .tmp_snap.txt | grep -E "listitem|StaticText"
```

봇도 사람도 같은 목록에 나온다. 중복 검사에 이걸 쓴다.

## 앱 목록 읽기 / 중복 검사

포털 `/developers/applications`:

```js
() => Array.from(document.querySelectorAll('a[href*="/developers/applications/"]'))
  .map(a => ({ name: a.innerText.trim().replace(/\n/g,' '),
               id: a.getAttribute('href').split('/').pop() }))
```

`name`에 아바타 이니셜이 앞에 붙는 경우가 있다(`"c-p content-pd"`). 이름 비교는 부분일치로 본다.

## 앱 생성

```
click(신규 애플리케이션 uid)
fill(이름 textbox uid, "<봇이름>")        ← fill 도구가 먹는다(일반 text input)
evaluate_script: 약관 체크박스 label 클릭  ← click 도구는 실패한다
click(만들기 uid)                          ← 체크 후에야 enabled가 된다
```

약관 체크 스니펫:

```js
() => { const inp = document.querySelector('[role="dialog"] input[type="checkbox"]');
        (inp.closest('label') || inp.parentElement).click(); }
```

체크됐는지는 `take_snapshot`에서 `checkbox ... checked`로 확인하는 게 가장 확실하다.

## CAPTCHA 대기

생성 직후 URL이 안 바뀌면 CAPTCHA일 수 있다. 판별:

```js
() => ({ url: location.href,
         captcha: document.body.innerText.includes('로봇 아니고 사람')
                  || !!document.querySelector('iframe[src*="hcaptcha"]') })
```

CAPTCHA면 `select_page(pageId, bringToFront: true)`로 탭을 띄우고 사용자에게 클릭을 요청한 뒤, **직접 풀지 말고 통과를 기다린다.** 한 번에 오래 기다리지 말고 아래를 여러 번 호출한다(호출당 약 25초):

```js
async () => { for (let i=0;i<50;i++){ if(/applications\/\d+/.test(location.href)) break;
                                      await new Promise(r=>setTimeout(r,500)); }
              return { url: location.href, done: /applications\/\d+/.test(location.href) }; }
```

`done:true`면 그대로 이어간다. 6~7회(약 3분) 넘게 안 풀리면 멈추고 다시 요청한다.

## Intent 켜고 저장·검증

`/applications/<APP_ID>/bot`. 이름으로 스위치를 찾는다(`Presence Intent`, `Server Members Intent`, `Message Content Intent`):

```js
async () => {
  const get = (name) => {
    const h = Array.from(document.querySelectorAll('h2,h3,div'))
      .find(e => e.textContent.trim() === name);
    if (!h) return null;
    let n = h.parentElement, inp = null, hops = 0;
    while (n && hops < 5) { inp = n.querySelector('input[type="checkbox"]'); if (inp) break; n = n.parentElement; hops++; }
    return inp;
  };
  for (let i=0;i<20;i++){ if(get('Message Content Intent')) break; await new Promise(r=>setTimeout(r,500)); }

  // 모드 A: 아래 둘. 모드 B: 'Message Content Intent' 하나만.
  for (const name of ['Server Members Intent','Message Content Intent']) {
    const inp = get(name);
    if (inp && !inp.checked) { (inp.closest('label')||inp.parentElement).click(); await new Promise(r=>setTimeout(r,400)); }
  }
  await new Promise(r=>setTimeout(r,400));
  const save = Array.from(document.querySelectorAll('button')).find(x=>x.textContent.trim()==='변경 사항 저장');
  if (save) save.click();
  await new Promise(r=>setTimeout(r,2500));
  return { toast: document.body.innerText.includes('성공적으로 업데이트'),
           intents: ['Presence Intent','Server Members Intent','Message Content Intent']
                      .map(n=>({name:n, checked:get(n)?.checked})) };
}
```

**저장 확인은 토스트만 믿지 않는다.** `navigate_page(type:"reload")` 후 위 `get()` 부분만 다시 돌려 값을 읽는다. 저장 배너가 DOM에 남아 있어 "저장 안 됨"으로 잘못 읽히는 경우가 있으니, 판단 근거는 **리로드 후 상태**로 한다.

## OAuth2 URL Generator

`/applications/<APP_ID>/oauth2`. 스코프와 권한이 전부 라벨 있는 체크박스라 같은 `label.click()` 패턴을 쓴다:

```js
async () => {
  const pick = (name) => {
    for (const i of document.querySelectorAll('input[type="checkbox"]')) {
      const lab = i.closest('label');
      if (lab && lab.textContent.trim() === name) { if (!i.checked) lab.click(); return true; }
    }
    return false;
  };
  for (let i=0;i<20;i++){ if(document.querySelectorAll('input[type="checkbox"]').length>10) break; await new Promise(r=>setTimeout(r,500)); }

  pick('bot'); await new Promise(r=>setTimeout(r,500));
  pick('applications.commands');            // ← 모드 B에서는 이 줄을 뺀다
  await new Promise(r=>setTimeout(r,900));  // bot을 켜야 권한 목록이 나타난다

  for (const n of ['채널 보기','메시지 보내기','메시지 기록 보기','공개 스레드 만들기',
                   '스레드에서 메시지 보내기','링크 임베드','파일 첨부','반응 추가']) {
    pick(n); await new Promise(r=>setTimeout(r,350));
  }
  await new Promise(r=>setTimeout(r,800));
  return { checked: Array.from(document.querySelectorAll('input[type="checkbox"]'))
                      .filter(i=>i.checked).map(i=>i.closest('label')?.textContent.trim()),
           url: Array.from(document.querySelectorAll('input,textarea'))
                  .map(e=>e.value).find(v=>v&&v.includes('oauth2/authorize')) };
}
```

`url`의 `permissions=309237763136`을 눈으로 확인한다. 권한 라벨은 포털이 **`링크 임베드`**인데 승인 화면에서는 **`링크 첨부`**로 나온다 — 같은 권한이다.

## 초대 승인 흐름

생성된 URL로 **이미 디스코드 웹이 떠 있던 탭을** `navigate_page` 한다. 새 탭은 「Discord 앱을 여는 중」에서 멈춰 버튼조차 안 나오는 경우가 있다.

```js
async () => {
  for (let i=0;i<20;i++){
    const b = Array.from(document.querySelectorAll('button,a')).find(x=>x.textContent.trim()==='Discord로 계속하기');
    if (b) { b.click(); break; }
    if (document.body.innerText.includes('서버에 추가')) break;
    await new Promise(r=>setTimeout(r,700));
  }
  for (let i=0;i<20;i++){ if(document.body.innerText.includes('서버에 추가')) break; await new Promise(r=>setTimeout(r,700)); }
  const cb = document.querySelector('[role="combobox"]');
  return { text: document.body.innerText.slice(0,400),
           server: cb ? (cb.getAttribute('value') || cb.textContent.trim()) : null };
}
```

`server`가 **대상 서버**인지 확인한 뒤 `계속하기` → 표시된 권한 8개 확인 → `승인`. 둘 다 텍스트로 버튼을 찾아 `.click()`하면 된다. 끝나면 URL이 `/oauth2/authorized`로 바뀌고 「성공!」이 뜬다.

## 채널 만들기 (비공개)

대상 카테고리의 `+` 버튼을 찾아 연다. 카테고리가 여럿이면 `aria-label`로 고른다:

```js
async () => {
  const cat = Array.from(document.querySelectorAll('[aria-label]'))
    .find(e => e.getAttribute('aria-label') === '<카테고리명> (카테고리)');
  const container = cat.closest('li') || cat.parentElement.parentElement;
  const btn = container.querySelector('[aria-label="채널 만들기"]')
           || document.querySelector('[aria-label="채널 만들기"]');
  btn.click();
  await new Promise(r=>setTimeout(r,2000));
  return document.querySelector('[role="dialog"]').innerText.slice(0,400);
}
```

다이얼로그 상단에 `:<카테고리명>에 속해 있음`이 찍힌다 — **여기서 카테고리를 확인한다.**

이어서 이름·비공개·생성:

1. 이름은 `fill` 도구로 넣는다(스냅샷의 `textbox "채널 이름"` uid). 일반 text input이라 잘 먹는다.
2. `비공개 채널` 스위치는 **`input.click()`** 으로 켠다(위 「왜 click/fill이 실패하는가」 참조).
3. 다이얼로그를 `take_screenshot(pageId, uid)`로 찍어 스위치가 켜졌는지 눈으로 확인한다.
4. 비공개면 버튼이 **`다음`**으로 바뀐다. 누르면 멤버 선택 화면이 나오고, 헤더에 방금 지은 채널명이 찍힌다.
5. 봇을 고르고(옵션 텍스트는 `이름이름#1234앱` 형태) `채널 만들기`.

```js
async () => {
  const d = Array.from(document.querySelectorAll('[role="dialog"]')).pop();
  const o = Array.from(document.querySelectorAll('[role="option"]'))
    .find(x => x.textContent.trim().startsWith('<BOT_NAME><BOT_NAME>#'));
  o.click(); await new Promise(r=>setTimeout(r,900));
  Array.from(d.querySelectorAll('button')).find(x=>x.textContent.trim()==='채널 만들기').click();
  await new Promise(r=>setTimeout(r,4000));
  return { url: location.href };   // /channels/<GUILD_ID>/<새 CHANNEL_ID>
}
```

반환된 URL 끝이 **새 채널 ID**다. 봇을 여기서 넣었으면 「채널 권한에 봇 추가」는 건너뛰고 검증만 한다.

## 채널 권한에 봇 추가

**모달이 "보고 있는 채널"에 붙는다.** 반드시 대상 채널로 `navigate_page` 한 뒤 시작하고, 모달 헤더의 채널명을 확인한다.

```js
async () => {
  const id = '<CHANNEL_ID>';
  await new Promise(r=>setTimeout(r,3000));                       // 채널 로딩 대기
  const link = document.querySelector('a[href="/channels/<GUILD_ID>/'+id+'"]');
  const row = link.closest('li') || link.parentElement.parentElement;
  row.querySelector('[aria-label="채널 편집"]').click();            // 사이드바 톱니
  await new Promise(r=>setTimeout(r,2200));
  Array.from(document.querySelectorAll('[role="tab"]')).find(t=>t.textContent.trim()==='권한').click();
  await new Promise(r=>setTimeout(r,1800));
  Array.from(document.querySelectorAll('button')).find(x=>x.textContent.trim()==='멤버 또는 역할 추가').click();
  await new Promise(r=>setTimeout(r,1500));
  const modal = Array.from(document.querySelectorAll('[role="dialog"]')).pop();
  return { modalHeader: modal ? modal.innerText.slice(0,60) : 'none' };  // ← 여기서 채널명 확인
}
```

`modalHeader`가 대상 채널명이 **아니면 즉시 중단**하고 채널을 다시 연다.

이어서 선택과 확정:

```js
async () => {
  // 옵션 텍스트는 "tech-qatech-qa#8529앱" 형태로 이름이 두 번 붙는다.
  // 같은 이름의 "tech-qa역할" 항목이 따로 있으니 반드시 #디스크리미네이터+앱 쪽을 고른다.
  const o = Array.from(document.querySelectorAll('[role="option"]'))
    .find(x => new RegExp('^<BOT_NAME><BOT_NAME>#\\d+앱$').test(x.textContent.trim()));
  if (!o) return 'option not found';
  o.click();                                   // aria-selected=true 가 된다
  await new Promise(r=>setTimeout(r,800));
  Array.from(document.querySelectorAll('button')).find(x=>x.textContent.trim()==='완료').click();
  await new Promise(r=>setTimeout(r,2500));
  return document.querySelector('[role="dialog"]').innerText.slice(0,700);   // 멤버 목록 확인
}
```

옵션만 클릭하고 `완료`를 안 누르면 **아무 일도 일어나지 않는다.** 반환된 텍스트의 `멤버` 이후에 봇이 보이는지 확인한다.

봇 이름에 정규식 특수문자(`.`, `-` 등)가 들어갈 수 있으니, 불안하면 정규식 대신 `x.textContent.trim().startsWith(name+name+'#')`로 비교한다.

## 잘못 넣은 권한 제거

해당 멤버 줄의 `제거하기` 버튼(스냅샷에서 봇 이름 바로 아래에 있다)을 `click`하면 확인 대화상자가 뜬다:

```js
async () => { const b = Array.from(document.querySelectorAll('button')).find(x=>x.textContent.trim()==='확인');
              b.click(); await new Promise(r=>setTimeout(r,2500));
              return document.querySelector('[role="dialog"]').innerText.slice(0,700); }
```

「권한 설정 삭제하기 — 이 작업은 취소할 수 없어요」가 뜨는데, 이건 **내가 방금 추가한 오버라이트를 지우는 것**이라 원상복구가 맞다. 다만 **다른 사람·봇의 항목에는 절대 쓰지 않는다.**

## 채널 권한 최종 검증

리로드 후 채널별로 멤버 목록만 뽑아 읽는다:

```js
async () => {
  await new Promise(r=>setTimeout(r,2800));
  const id='<CHANNEL_ID>';
  const link=document.querySelector('a[href="/channels/<GUILD_ID>/'+id+'"]');
  const row=link.closest('li')||link.parentElement.parentElement;
  row.querySelector('[aria-label="채널 편집"]').click();
  await new Promise(r=>setTimeout(r,2200));
  Array.from(document.querySelectorAll('[role="tab"]')).find(t=>t.textContent.trim()==='권한').click();
  await new Promise(r=>setTimeout(r,1800));
  const txt=document.querySelector('[role="dialog"]').innerText;
  return { channel: txt.slice(0,14),
           desynced: txt.includes('동기화되지 않은 권한'),
           members: (txt.split('멤버\n')[1]||'').replace(/\n/g,' ').slice(0,260) };
}
```

채널을 옮길 때는 `press_key(Escape)`로 설정을 닫고 `navigate_page`로 이동한다. **한 `evaluate_script` 안에서 `location.href`로 이동하면 "Execution context was destroyed"가 난다** — 채널마다 호출을 나눈다.

`desynced`는 손댄 결과가 아니라 원래 값일 수 있다. 작업 **전에** 한 번 읽어 두면 나중에 비교할 수 있다.

## UI 라벨 대응표

포털 언어 설정에 따라 달라진다. 한국어 기준으로 적었으니 영어 UI면 아래로 바꿔 읽는다.

| 한국어 | English |
|---|---|
| 신규 애플리케이션 | New Application |
| 만들기 | Create |
| 변경 사항 저장 | Save Changes |
| 초기화 | Reset |
| 토큰 초기화 | Reset Token |
| 봇 / 설치 / OAuth2 | Bot / Installation / OAuth2 |
| 채널 편집 | Edit Channel |
| 권한 | Permissions |
| 멤버 또는 역할 추가 | Add members or roles |
| 완료 / 취소 / 확인 | Done / Cancel / Confirm |
| 제거하기 | Remove |
| 지금 동기화하기 | Sync Now (**누르지 말 것**) |
| 채널 보기 | View Channels |
| 메시지 보내기 | Send Messages |
| 메시지 기록 보기 | Read Message History |
| 공개 스레드 만들기 | Create Public Threads |
| 스레드에서 메시지 보내기 | Send Messages in Threads |
| 링크 임베드 (승인화면: 링크 첨부) | Embed Links |
| 파일 첨부 | Attach Files |
| 반응 추가 | Add Reactions |
| Discord로 계속하기 | Continue to Discord |
| 서버에 추가 | Add to Server |
| 승인 / 계속하기 | Authorize / Continue |
