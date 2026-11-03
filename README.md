<div align="center">

<img src="logo.png" alt="Graniton Logo" width="160" height="160" style="border-radius: 28%;" />

# Graniton Messenger — Uncensored Edition 🔓

**Повністю розблокована модифікація Telegram для Android (`гілка uncensored`) без цензури Google Play та вікових обмежень, із фіолетовою енергетичною палітрою, повним контролем приватності та оптимізацією під Samsung Galaxy S26 Ultra.**

[![Build Graniton Uncensored Android](https://github.com/Gladiator666Satan/Graniton/actions/workflows/build.yml/badge.svg?branch=uncensored)](https://github.com/Gladiator666Satan/Graniton/actions/workflows/build.yml)
[![Edition](https://img.shields.io/badge/Edition-Uncensored%20%2F%20Direct-ff2e93.svg)](https://github.com/Gladiator666Satan/Graniton/tree/uncensored)
[![Architecture](https://img.shields.io/badge/Architecture-arm64--v8a-8a2be2.svg)](https://github.com/Gladiator666Satan/Graniton)
[![Optimized For](https://img.shields.io/badge/Optimized%20For-Samsung%20Galaxy%20S26%20Ultra-0d0214.svg)](https://github.com/Gladiator666Satan/Graniton)
[![Base](https://img.shields.io/badge/Telegram%20Android-v13.1.1-2CA5E0.svg)](https://telegram.org)

[📥 **Завантажити Graniton Uncensored APK у Releases**](https://github.com/Gladiator666Satan/Graniton/releases)

---

</div>

## ⚖️ Дві редакції застосунку (Standard vs Uncensored)

Проєкт **Graniton** підтримується у двох незалежних гілках та випускає два типи релізів, підписаних єдиним RSA-ключем (`org.graniton.messenger`), щоб ви могли вільно оновлюватися або перемикатися між ними поверх встановленого додатка **без втрати акаунта та історії чатів**:

| Редакція | Гілка | Файл релізу APK | Особливості |
| :--- | :--- | :--- | :--- |
| **🔒 Graniton Standard** *(з цензурою)* | [`master`](https://github.com/Gladiator666Satan/Graniton/tree/master) | `Graniton-arm64-v8a.apk` | Увесь функціонал Power-Pack зі збереженням стандартних контентних фільтрів платформи Google Play. |
| **🔓 Graniton Uncensored** *(без цензури)* | [`uncensored`](https://github.com/Gladiator666Satan/Graniton/tree/uncensored) | `Graniton-Uncensored-arm64-v8a.apk` | Повне зняття блокувань Google Play (`android`, `android-all`, `all`), розблокування `18+ / Sensitive` каналів і медіа та обхід вікової відео-верифікації. |

---

## 🔓 Що додатково розблоковано в гілці `uncensored`

* 🚫 **Обхід блокувань Google Play Store (`MessagesController.getRestrictionReason`)**:
  * Канали, чати, боти, міні-додатки та окремі повідомлення, які в клієнтах із Play Маркету блокуються повідомленням *«Цей канал не може бути відображений, оскільки його не можна переглядати в застосунках Telegram, завантажених із Google Play»* (`platform: "android"`, `"android-all"`, `"all"`), відкриваються напряму без жодних обмежень чи текстових заглушок.
* 🔞 **Повний доступ до `18+ / Sensitive Content` без примусового блюру**:
  * Вимкнено вікна попередження під час входу в чутливі канали (`MessagesController.isSensitive`) та примусове розмиття медіа з позначкою *«Чутливий контент»* (`MessageObject.isSensitive`, `isHiddenSensitive`), при цьому звичайні користувацькі спойлери (`media.spoiler`) працюють штатно.
* 🪪 **Обхід вікової відео-верифікації (`ThemeActivity.verifyAge`)**:
  * Вимкнено примусовий виклик бота перевірки віку з Telegram v13.1+.
* 📡 **Direct / Non-Store MTProto ініціалізація (`ConnectionsManager.init`)**:
  * При підключенні до серверів MTProto очищується ідентифікатор магазину встановлення (`installer = ""`), щоб сервер сприймав клієнт як пряму Direct-збірку зі збереженням 100% сумісності з Play Integrity та Firebase Push.

---

## ⚡ Ексклюзивний функціонал Graniton Power-Pack

* 💣 **Stealth-перегляд, збереження та скриншоти «бомбочок» (View-Once / TTL)**:
  * **Анонімне відкриття зі збереженням таймера**: На розмитому прев'ю в чаті коректно відображається бейдж таймера (`1`, `5s`, `10s`), але при відкритті блокується відправка звітів про перегляд (`sendSecretMessageRead`, `markMessageContentAsRead`) та команда самознищення (`sendSecretMediaDelete`). У відправника фото, відео, одноразове голосове чи кружечок залишаються **невідкритими** й не зникають із чату.
  * **Пряме збереження та AES-дешифрування `.enc`**: У переглядачі `SecretMediaViewer` додано кнопку збереження в галерею; вимкнено локальне `.enc`-шифрування кешу для нових файлів, а для вже зашифрованих реалізовано прозоре розшифрування (`EncryptedFileInputStream`) і резервне збереження `Bitmap` із пам'яті. Доступне збереження й через довге натискання в чаті (включно з Secret Chats).
  * **Повне зняття `FLAG_SECURE`**: Дозволено створення скриншотів та запис екрана у переглядачі зникаючих медіа, таємних чатах, захищених каналах та на екрані блокування.
* 🎥 **Чесні HD 60fps кружечки (Video Notes)**: Запис нативних круглих відеоповідомлень `384×384` при **60 кадрах/с** зі студійним бітрейтом **2.5 Мбіт/с** (замість стандартних `30fps` / `1.0 Мбіт/с`).
* 📸 **HD 1080p відео за замовчуванням**: У `PhotoViewer` знято стандартне обмеження 720p (`maxCompression = 2`) — при відправці відео автоматично обирається максимальний HD-профіль якості.
* 🙈 **Коректні медіа-спойлери (`hasMediaSpoilers`)**: Виправлено передачу прапорця прихованого контенту на сервери MTProto при надсиланні одиночних і групових фото та відео.
* 🌐 **Живий переклад чатів та повідомлень + Ad-Free**: Розблоковано верхню панель автоматичного перекладу всього чату та кнопку перекладу в контекстному меню з безкоштовним клієнтським фолбеком без підписки Premium, а також вимкнено спонсорську рекламу в каналах.
* 🕵️ **True Ghost Mode (Режим «Привид»)**: Повне приховування активності введення (`sendTyping`) та локальне скидання лічильника згадок `@` без відправки звіту серверу.
* 🛡️ **Anti-Delete Protection**: Ігнорування вхідних команд видалення — повідомлення залишаються у вашій локальній історії чату, навіть якщо їх видалили «для всіх».
* 🔓 **Bypass Restricted Content (`noforwards`)**: Повне зняття обмежень на збереження медіа, поширення файлів, копіювання тексту/коду та пересилання із захищених каналів.
* ⚡ **Force 120Hz Fluidity**: Апаратне блокування максимальної частоти оновлення дисплея (**120Hz**) для Dynamic AMOLED 2X екранів Samsung Galaxy S26 Ultra.

---

## ✨ Фірмовий дизайн, брендинг та системна інтеграція

* **Векторний логотип GRANITON у шапці**: Геометрично вивірений векторний логотип **GRANITON** (`telegram_logo_2.xml` із правилом заливки `evenOdd`) у шапці чатів та блоці Stories.
* **Dark Violet / Purple Energy Theme за замовчуванням**: Глибока нічна палітра (`#0d0214`, `#08000c`, `#160926`) із неоново-фіолетовими акцентами (`#8b2be2` / `#9333ea`).
* **Безшовне брендування Samsung One UI**: Сповіщення з акцентом `#8b2be2` та підписом **Graniton** (`android.substName`), українське й англійське брендування вікон біометрії/PIN-коду (`LocaleController`), сервісні чати `Graniton Notifications` / `Graniton Support` та збереження медіа у власні альбоми `Graniton`.

---

## 🎨 Фірмова тема: Graniton Dark Violet (`.attheme`)

* [`themes/Graniton_Dark_Violet.attheme`](themes/Graniton_Dark_Violet.attheme) — еталонна тема Graniton
* [`themes/DarkViolet.attheme`](themes/DarkViolet.attheme) — адаптована й збалансована тема DarkViolet

---

## 📥 Встановлення (Installation Guide)

1. Перейдіть у розділ [**Releases**](https://github.com/Gladiator666Satan/Graniton/releases).
2. Оберіть потрібну редакцію:
   * **`Graniton-Uncensored-arm64-v8a.apk`** — версія **без цензури** (з гілки `uncensored`).
   * **`Graniton-arm64-v8a.apk`** — стандартна версія **з цензурою** (з гілки `master`).
3. Відкрийте завантажений файл на смартфоні та підтвердьте встановлення (можна встановлювати поверх вже встановленого Graniton без виходу з акаунта).

> [!NOTE]
> **Під час встановлення на Samsung One UI:**
> * **Google Play Protect**: Натисніть **«Детальніше» (More details) ➔ «Все одно встановити» (Install anyway)**.
> * **Samsung Auto Blocker**: Тимчасово вимкніть *Налаштування ➔ Безпека та конфіденційність ➔ Автоблокування* на час інсталяції APK.

---

## ⚖️ Ліцензія

Цей проєкт базується на відкритому вихідному коді [Telegram for Android](https://github.com/DrKLO/Telegram) та розповсюджується на умовах ліцензії [GNU General Public License v2/v3](LICENSE).
