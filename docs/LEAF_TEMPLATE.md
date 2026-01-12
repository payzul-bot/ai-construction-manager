# AI Construction Platform — Leaf Work Template

## 1. Назначение документа

Этот документ описывает **универсальный шаблон Leaf-работы**  
(атомарной, неделимой работы), используемый в AI Construction Platform.

Leaf-работа:
- имеет собственный CalculationProfile;
- считается детерминированно;
- не зависит от UX и LLM;
- является минимальной единицей расчёта.

Любая новая работа в платформе **обязана** быть описана по этому шаблону.

---

## 2. Общие принципы Leaf-работ

1. Одна Leaf = один CalculationProfile.
2. Leaf не содержит UI-логики.
3. Leaf не содержит свободного текста.
4. Leaf использует только канонические ID.
5. Изменение Leaf = новая версия профиля.

---

## 3. Идентификация Leaf-работы

- work_id — канонический идентификатор (immutable)
- name — каноническое название (для UI)
- category — тип работ (demolition / construction / finishing / installation)
- description — краткое инженерное описание

Пример:
- work_id: paint_walls_putty
- name: Покраска стен по шпаклёвке
- category: finishing

---

## 4. Область применения

Описание условий, при которых Leaf-работа допустима.

- типы объектов;
- типы оснований;
- ограничения по среде;
- региональные особенности (если есть).

Если условия не выполняются — работа блокируется Rule Engine.

---

## 5. Входные параметры (Params)

Список **обязательных и опциональных параметров**.

Для каждого параметра:
- param_id
- type (number / enum / boolean)
- required (true / false)
- допустимые значения или диапазоны
- краткое описание

Пример:
- param_id: wall_area
  type: number
  required: true
  min: 0
  max: 10000
  description: Площадь стен, м²

---

## 6. Формулы расчёта (Formulas)

Описание формул для вычисления объёмов.

Для каждой формулы:
- formula_id
- expression (детерминированное выражение)
- unit (единица результата)

Пример:
- formula_id: paint_volume
- expression: wall_area * layers * consumption_rate
- unit: liter

Формулы:
- не содержат условий UX;
- используют только параметры и коэффициенты.

---

## 7. BOM (Материалы / Инструменты / Оборудование)

Список ресурсов, используемых в Leaf-работе.

Для каждого элемента BOM:
- resource_id
- resource_type (material / tool / equipment)
- unit
- quantity_formula
- допустимые классы качества
- условия включения (если есть)

Пример:
- resource_id: paint_interior
- resource_type: material
- unit: liter
- quantity_formula: paint_volume
- quality_classes: comfort, business, premium
- condition: layers > 1

---

## 8. Правила и запреты (Rules)

Список правил, применяемых Rule Engine.

Типы правил:
- validation
- inclusion
- block
- conditional
- escalation

Для каждого правила:
- rule_type
- condition
- message

Пример:
- rule_type: block
- condition: base_is_wet == true
- message: Нельзя выполнять покраску по влажному основанию

---

## 9. Контроль качества (QC)

Обязательные проверки качества для Leaf-работы.

Для каждого QC-пункта:
- qc_id
- stage_id
- check
- severity (required / warning)

Пример:
- qc_id: surface_dry
- stage_id: preparation
- check: Поверхность сухая и очищена от пыли
- severity: required

---

## 10. Этапы выполнения (Stages)

Описание логических этапов выполнения Leaf-работы.

Для каждого этапа:
- stage_id
- name
- order_index

Пример:
- stage_id: preparation
- name: Подготовка поверхности
- order_index: 1

---

## 11. Выходные данные Leaf-работы (Outputs)

Leaf-работа возвращает:
- рассчитанные объёмы;
- список ресурсов;
- QC-пункты;
- выявленные риски;
- статус (allowed / blocked / conditional).

Leaf **не формирует**:
- цены;
- закупку;
- сроки проекта целиком.

---

## 12. Версионирование Leaf-работ

Любое изменение:
- параметров;
- формул;
- BOM;
- правил;
- QC;

создаёт **новую версию CalculationProfile**.

Старые версии сохраняются для:
- аудита;
- сравнения;
- воспроизводимости.

---

## 13. Связь с другими слоями

Leaf-работа используется:
- Orchestration Layer (план работ);
- Core Engine (расчёт);
- UX (только отображение);
- Import Layer (предзаполнение параметров).

Leaf не зависит от:
- UI;
- LLM;
- конкретного пользователя.

---

## 14. Типовые ошибки при создании Leaf

Запрещено:
- объединять несколько работ в одну Leaf;
- использовать свободный текст вместо ID;
- добавлять скрытые условия;
- делать расчёт недетерминированным;
- хранить логику в UI.

---

## 15. Статус документа

Этот шаблон:
- обязателен для описания всех Leaf-работ;
- используется как эталон;
- изменяется крайне редко.