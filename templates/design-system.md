# Design System

**Проект:** [Название проекта]
**UI-kit:** shadcn/ui / Chakra UI / Material UI
**Дата:** [YYYY-MM-DD]
**Автор:** Designer

---

## Подход

Code-first: дизайн-система реализуется сразу в коде, без отдельного дизайн-инструмента.

---

## Токены

### Цвета

```css
:root {
  /* Primary */
  --color-primary-50: #f0f9ff;
  --color-primary-100: #e0f2fe;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  
  /* Neutral */
  --color-neutral-50: #fafafa;
  --color-neutral-100: #f5f5f5;
  --color-neutral-500: #737373;
  --color-neutral-900: #171717;
  
  /* Semantic */
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;
}
```

### Типографика

```css
:root {
  /* Font Family */
  --font-sans: Inter, system-ui, sans-serif;
  --font-mono: JetBrains Mono, monospace;
  
  /* Font Size */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  
  /* Font Weight */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* Line Height */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### Отступы

```css
:root {
  --spacing-0: 0;
  --spacing-1: 0.25rem;   /* 4px */
  --spacing-2: 0.5rem;    /* 8px */
  --spacing-3: 0.75rem;   /* 12px */
  --spacing-4: 1rem;      /* 16px */
  --spacing-5: 1.25rem;   /* 20px */
  --spacing-6: 1.5rem;    /* 24px */
  --spacing-8: 2rem;      /* 32px */
  --spacing-10: 2.5rem;   /* 40px */
  --spacing-12: 3rem;     /* 48px */
}
```

### Тени

```css
:root {
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}
```

### Border Radius

```css
:root {
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-full: 9999px;
}
```

---

## Компоненты

### Button

**Расположение:** `src/design-system/components/Button.tsx`

**Варианты:**
- Variant: `primary`, `secondary`, `outline`, `ghost`
- Size: `sm`, `md`, `lg`
- State: `default`, `loading`, `disabled`

**Пример использования:**
```tsx
<Button variant="primary" size="md">
  Нажать
</Button>
```

---

### Input

**Расположение:** `src/design-system/components/Input.tsx`

**Варианты:**
- Size: `sm`, `md`, `lg`
- State: `default`, `error`, `disabled`

---

### Card

**Расположение:** `src/design-system/components/Card.tsx`

---

### Modal

**Расположение:** `src/design-system/components/Modal.tsx`

---

## Иконки

**Библиотека:** Lucide Icons

**Использование:**
```tsx
import { Home, Settings, User } from 'lucide-react';
```

---

## Структура файлов

```
src/design-system/
├── tokens.css           # CSS-переменные
├── theme.ts             # Tailwind/theme конфиг
└── components/
    ├── Button.tsx
    ├── Input.tsx
    ├── Card.tsx
    ├── Modal.tsx
    └── index.ts         # Экспорт всех компонентов
```

---

## Changelog

| Дата | Изменение | Автор |
|------|-----------|-------|
| YYYY-MM-DD | Initial design system | Designer |
