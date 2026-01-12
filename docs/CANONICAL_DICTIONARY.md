# AI Construction Platform — Canonical Dictionary

## 1. Назначение документа

Canonical Dictionary — это **единый источник истины** для всех канонических
названий и идентификаторов платформы.

Документ фиксирует:
- канонические ID работ, ресурсов и этапов;
- человеко-читаемые названия;
- типы и категории;
- инварианты, которые нельзя нарушать.

Любая логика платформы оперирует **ID**, а не свободным текстом.
Текст используется только как слой представления.

---

## 2. Общие правила словаря

1. Каждый элемент имеет **уникальный канонический ID**.
2. ID не меняется после публикации.
3. Переименование возможно только через новый ID.
4. Запрещены синонимы на уровне логики.
5. Все расчёты, правила и версии используют только ID.

---

## 3. Типы сущностей словаря

- WorkLeaf — атомарная работа
- Resource — материал / инструмент / оборудование
- Stage — этап выполнения
- QCItem — пункт контроля качества
- Risk — типовой риск
- Unit — единица измерения

---

## 4. WorkLeaf (канонические работы)

WorkLeaf — минимальная неделимая работа, которая:
- имеет собственный CalculationProfile;
- может быть посчитана и проверена;
- не содержит логики внутри UI или LLM.

### 4.1 Формат WorkLeaf

- work_id — канонический ID
- name — каноническое название
- category — тип работ
- description — краткое описание

### 4.2 Примеры WorkLeaf

- work_id: paint_walls_putty  
  name: Покраска стен по шпаклёвке  
  category: finishing  
  description: Финишная покраска подготовленных стен

- work_id: prime_walls  
  name: Грунтование стен  
  category: finishing  
  description: Нанесение грунтовки перед отделочными работами

- work_id: remove_old_paint  
  name: Удаление старой краски  
  category: demolition  
  description: Механическое или химическое удаление покрытия

---

## 5. Resource (ресурсы)

Resource — всё, что используется для выполнения работ.

### 5.1 Типы ресурсов

- material
- tool
- equipment

### 5.2 Формат Resource

- resource_id — канонический ID
- name — каноническое название
- type — material / tool / equipment
- unit — единица измерения
- quality_classes — допустимые классы качества

### 5.3 Примеры материалов

- resource_id: paint_interior  
  name: Краска интерьерная  
  type: material  
  unit: liter  
  quality_classes: economy, comfort, business, premium

- resource_id: primer_universal  
  name: Грунтовка универсальная  
  type: material  
  unit: liter  
  quality_classes: economy, comfort, business, premium

### 5.4 Примеры инструментов

- resource_id: roller_standard  
  name: Валик малярный  
  type: tool  
  unit: piece  
  quality_classes: economy, comfort, business, premium

- resource_id: ladder_aluminum  
  name: Стремянка алюминиевая  
  type: tool  
  unit: piece  
  quality_classes: economy, comfort, business, premium

---

## 6. Stage (этапы работ)

Stage описывает логический этап выполнения работы.

### 6.1 Формат Stage

- stage_id
- name
- order_index

### 6.2 Примеры Stage

- stage_id: preparation  
  name: Подготовка поверхности  
  order_index: 1

- stage_id: application  
  name: Нанесение материала  
  order_index: 2

- stage_id: finishing  
  name: Завершение работ  
  order_index: 3

---

## 7. QCItem (контроль качества)

QCItem — обязательный пункт контроля, возвращаемый ядром.

### 7.1 Формат QCItem

- qc_id
- stage_id
- check
- severity

### 7.2 Примеры QCItem

- qc_id: surface_dry  
  stage_id: preparation  
  check: Поверхность сухая и очищена от пыли  
  severity: required

- qc_id: uniform_color  
  stage_id: finishing  
  check: Равномерность цвета без пропусков  
  severity: required

---

## 8. Risk (риски)

Risk — типовой риск, выявляемый Rule Engine.

### 8.1 Формат Risk

- risk_id
- name
- description
- severity

### 8.2 Примеры Risk

- risk_id: wet_base  
  name: Влажное основание  
  description: Основание не высохло перед началом работ  
  severity: high

- risk_id: poor_adhesion  
  name: Плохая адгезия  
  description: Возможное отслаивание покрытия  
  severity: medium

---

## 9. Unit (единицы измерения)

Единицы измерения используются во всех расчётах.

### 9.1 Примеры Unit

- unit_id: meter  
  name: метр  

- unit_id: square_meter  
  name: квадратный метр  

- unit_id: liter  
  name: литр  

- unit_id: piece  
  name: штука  

---

## 10. Связь со всеми слоями платформы

Canonical Dictionary используется:
- CalculationProfile
- Rule Engine
- Engine Result
- Versioning
- Audit
- UI (только для отображения)

UI и LLM **не имеют права**:
- создавать новые ID;
- менять существующие названия;
- использовать синонимы.

---

## 11. Эволюция словаря

Допустимо:
- добавление новых WorkLeaf;
- добавление новых Resource;
- добавление новых Stage и QCItem.

Недопустимо:
- изменение существующих ID;
- удаление используемых элементов;
- замена ID без миграции.

---

## 12. Статус документа

Этот документ:
- является обязательным для всей платформы;
- расширяется по мере роста предметной области;
- меняется только через контролируемые версии.
