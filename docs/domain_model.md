Nook Domain Model 🌿

## Modeling Principles

### 1. Reality First

Nook models the real world first.

We do not start from pages, buttons, or database tables.  
We first ask:

> What exists in the real world?

### 2. Entity Before UI

A new feature should first identify its entities and events.

We do not create a table just because a page needs a dropdown.  
The UI should grow from the domain model.

### 3. Every Attribute Has One Owner

An attribute belongs to the entity that naturally owns it.

Examples:

- `expiry_date` belongs to `Supplement Bottle`, not `Supplement`.
- `teacher_name` belongs to `Teacher`, not directly to `Ballet Lesson`.
- `food_category` belongs to `Food`, not `Meal`.

### 4. Event Records What Happened

Most trackers are event recorders.

Examples:

- Supplement Intake
- Meal
- Ballet Lesson
- Fermentation Observation
- Daily Health Log

For every event, ask:

> When did it happen?  
> Who or what was involved?

Nook is modeled from real-world entities, not from UI pages.

Principle:

Reality first. Database second. UI third.

⸻

Core Domains

Today

Today is not a domain entity.
It is a view that summarizes events, states, and attention items from all domains.

⸻

Health Domain

Entities

Person

A real person using or being tracked in Nook.

Examples:

* Vera
* Pingping

Supplement

A type of supplement.

Examples:

* Magnesium Glycinate
* Vitamin D3
* NAC
* Selenium

A Supplement is not the same as a physical bottle.

Supplement Bottle

A physical bottle or package of a supplement.

Attributes may include:

* supplement
* brand
* product name
* strength
* quantity
* purchase date
* expiry date
* opened date
* finished date
* purchase place
* notes

Supplement Intake

An event where a person takes a supplement.

Relationships:

* belongs to one person
* may refer to one supplement bottle
* happens at a specific time

Period Cycle

A menstrual cycle record.

Attributes:

* start date
* end date
* flow level
* notes

Daily Health Log

A daily record of body status.

Attributes:

* date
* sleep
* energy
* stress
* mood
* pain
* notes

⸻

Home Domain

Entities

Food

A general food concept.

Examples:

* Blueberry
* Beef
* Rice

Inventory Item

A specific physical item in the home.

Example:

* one box of blueberries in the fridge

Attributes:

* food/item name
* category
* location
* quantity
* purchase date
* expiry date
* notes

Meal

An eating event.

Attributes:

* date
* meal type
* content
* notes

Chore

A household task.

Attributes:

* title
* created time
* completed status
* completed by
* completed time

⸻

Fermentation Domain

Entities

Fermentation Batch

A specific fermentation project.

Examples:

* Kombucha batch started on 2026-07-01
* Yogurt batch
* Pickles batch

Attributes:

* batch name
* start date
* status
* liquid volume
* ingredients
* notes

Fermentation Observation

An observation event during fermentation.

Attributes:

* batch
* observation time
* smell
* appearance
* action taken
* notes

⸻

Ballet Domain

Entities

Teacher

A ballet teacher.

Studio

A ballet institution or location.

Ballet Lesson

A class event.

Relationships:

* happens at one time
* may have one teacher
* may happen at one studio

Attributes:

* date
* start time
* duration
* city
* address
* class type
* level
* notes

Correction

A teacher correction or personal learning note.

Relationships:

* may belong to one lesson
* may belong to one teacher
* may refer to one body part or technique topic

⸻

Library Domain

Library stores reusable reference data.

Examples:

* meal types
* inventory categories
* inventory locations
* ballet levels
* ballet class types
* moods
* symptoms

Important rule:

If something has rich attributes and lifecycle, it should become a real Entity, not just a Library option.

Example:

* Supplement should be an Entity.
* Meal Type can stay a Library option.

# Supplement Domain

## Entities

- Person
- Supplement
- Supplement Bottle

## Events

- Purchase
- Supplement Intake
- Open Bottle
- Finish Bottle

## Relationships

Person
    performs
        ↓
Supplement Intake
    uses
        ↓
Supplement Bottle
    instance of
        ↓
Supplement

## Lifecycle

Supplement Bottle

Purchase
↓

Open
↓

Use
↓

Finish
↓

Discard