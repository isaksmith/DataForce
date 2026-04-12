# MiroFish Integration Plan for Customer Behavior Simulation

## Goal
Integrate `MiroFish` with the existing `DataForce` banking datasets to simulate realistic customer behavior, friction events, support escalation, and intervention outcomes. The target deliverable is a scenario simulation workflow that turns structured CSV records into customer personas, event sequences, and multi-agent experiments that help predict which interventions reduce friction and support cost.

## Why this integration makes sense
`DataForce` already has the ingredients for behavior modeling:
- `customers.csv` provides customer profile context such as segment, tenure, products held, branch, digital enrollment timing, and churn status.
- `digital_sessions.csv` provides behavioral traces across channels, features, outcomes, and error events.
- `support_interactions.csv` provides escalation behavior after friction.
- `error_codes.csv` explains failure semantics.
- `feature_costs.csv` provides operational and feature-risk context.
- `friction_score_pipeline.py` already engineers retry patterns, failure streaks, support follow-up indicators, and interpretable risk signals.

`MiroFish` adds a simulation layer on top of that foundation by allowing:
- persona-driven customer agents
- scenario-based intervention testing
- repeated simulation under alternate product/support strategies
- synthetic but grounded forecasts for customer journeys

## Primary simulation objective
Simulate how different customer segments behave during digital banking journeys and estimate how likely they are to:
1. complete a task successfully
2. abandon after friction
3. retry the same feature
4. escalate to support
5. churn or remain engaged
6. respond positively to proactive interventions

## Recommended use cases

### 1. Friction-to-support escalation simulation
Model which customer profiles are most likely to contact support after failed login, transfer, bill pay, or mobile deposit sessions.

### 2. Intervention strategy simulation
Compare outcomes for:
- no intervention
- contextual tooltip
- guided tutorial
- chatbot interception
- direct human escalation

### 3. Segment behavior simulation
Run separate simulations for:
- `Retail`
- `SMB`
- `Student`
- `Wealth`
- `Unknown`

This helps quantify how segment-specific UX or support policies change session outcomes.

### 4. Churn-risk scenario simulation
Use friction history and support resolution patterns to simulate whether repeated high-friction experiences may push a customer toward churn.

## Data assets to feed into MiroFish

### Core entity table: customers
Use `customers.csv` as the base for agent personas.

Important fields:
- `customer_id`
- `tenure_months`
- `segment`
- `products_held`
- `digital_enroll_date`
- `home_branch`
- `churn_flag`

Derived persona attributes to create before simulation:
- `product_count_derived`
- `digital_experience_level` from tenure + enroll date + prior sessions
- `likely_feature_mix` from products held and session history
- `branch_dependency` based on branch association + support/branch visit patterns
- `churn_risk_proxy` from churn flag, friction, unresolved interactions

### Behavioral event table: sessions
Use `digital_sessions.csv` as the primary event history.

Expected fields from existing pipeline logic:
- `session_id`
- `customer_id`
- `channel`
- `feature_used`
- `session_start`
- `session_end`
- `session_outcome`
- `error_code`

Derived behavior features from `friction_score_pipeline.py`:
- `feature_canonical`
- `channel_norm`
- `session_outcome_norm`
- `has_error_code`
- `is_failure_like`
- `prior_session_count`
- `prior_same_feature_attempts_24h`
- `prior_same_feature_failures_24h`
- `prior_failed_streak_same_feature`
- `is_repeat_retry_pattern`
- `friction_score`
- `support_followup_24h`
- `support_followup_72h`

### Support escalation table
Use `support_interactions.csv` to model post-friction escalation.

Important fields:
- `interaction_type`
- `reason_code`
- `interaction_ts`
- `resolution_status`

Derived support traits:
- preferred support channel
- probability of unresolved issue
- likelihood of branch visit after digital failure
- escalation threshold after repeated failure

### Error semantics table
Use `error_codes.csv` to classify the meaning and severity of failures.

Suggested mappings:
- `AUTH_FAIL` → authentication barrier
- `TIMEOUT` → system instability
- `E010` → mobile deposit image issue
- `E020` → deposit limit barrier
- `E050` → expired session / interruption
- `E099` → rate limit / repeated behavior constraint

### Feature risk table
Use `feature_costs.csv` for simulation weighting.

Examples:
- High failure premium features should contribute more frustration.
- Features with expensive failed outcomes should have stronger support-escalation pressure.

## Proposed simulation design

## 1. Build a banking simulation ontology
Create a banking-specific schema that maps DataForce concepts into MiroFish entities.

### Agents
- customer agent
- support agent
- digital assistant agent
- branch agent
- system/feature environment agent

### Core objects
- banking feature
- session
- support ticket
- branch
- intervention
- friction event
- error event

### Relationships
- customer uses feature
- customer belongs to segment
- customer associated with branch
- session triggers error
- friction triggers support contact
- intervention modifies outcome

## 2. Create customer persona generation rules
Convert each row in `customers.csv` into a simulation persona.

### Persona template
Each agent should have:
- demographic/business segment
- digital maturity
- patience tolerance
- support-seeking tendency
- preferred channel
- trust in digital banking
- feature familiarity
- probability of retry after failure

### Suggested persona logic
Examples:
- `Student` + recent digital enrollment → high mobile preference, moderate patience, low branch preference
- `Wealth` + long tenure → high service expectations, lower tolerance for unresolved friction
- `SMB` + business products → high urgency around transfers and merchant services
- low tenure + low prior session count → novice digital user
- repeated unresolved interactions → low trust, high escalation tendency

## 3. Build journey archetypes from historical data
Before simulation, aggregate real behavior into journey archetypes such as:
- smooth success journey
- fail then retry success
- fail then support escalation
- repeated failure and abandonment
- unresolved support and churn-risk path

These archetypes should seed MiroFish scenarios so the simulated world starts from grounded patterns instead of generic narratives.

## 4. Define simulation states and transitions
Each customer journey can be modeled as a state machine:
- intent formed
- feature attempt started
- success
- failure with recoverable error
- failure with severe error
- retry
- abandonment
- support interaction
- resolution
- post-resolution retention or churn risk increase

Transition probabilities should be estimated from real data grouped by:
- segment
- feature
- channel
- error type
- prior failure history
- experience level

## 5. Inject DataForce friction scoring into simulation
Use `friction_score` as a control variable inside simulation.

Suggested behavior mapping:
- low friction: customer continues digital self-service
- medium friction: customer hesitates, retries, or needs explanation
- high friction: customer escalates to support, abandons task, or loses trust

This is the cleanest bridge between the existing rule-based analytics and MiroFish’s simulation engine.

## Implementation phases

### Phase 1: Data preparation and export
Create a preprocessing layer in `DataForce` that produces MiroFish-ready artifacts.

Recommended output files:
- `artifacts/customer_personas.json`
- `artifacts/session_journeys.json`
- `artifacts/support_patterns.json`
- `artifacts/feature_risk_lookup.json`
- `artifacts/error_taxonomy.json`
- `artifacts/simulation_seed_report.md`

Tasks:
- clean IDs and timestamps using existing normalization logic
- aggregate sessions by customer
- compute persona features
- build feature-by-segment behavior summaries
- summarize support escalation probabilities
- package scenario seeds in JSON/Markdown for MiroFish upload

### Phase 2: Scenario authoring for MiroFish
Create seed materials that explain the simulated world in natural language plus structured data.

Suggested scenario packs:
- retail mobile deposit failure scenario
- smb transfer outage scenario
- wealth customer high-expectation support scenario
- novice customer login recovery scenario
- repeated unresolved friction leading to churn scenario

Each scenario pack should include:
- business context
- participating agents
- initial state
- constraints
- intervention options
- success metrics

### Phase 3: MiroFish environment configuration
Inside `MiroFish`, configure:
- graph building inputs from the exported artifacts
- entity relationship extraction for customers, features, support, and branches
- persona generation prompts using the derived customer features
- simulation config templates for bank journeys
- report templates focused on friction, cost, and retention outcomes

Likely files to customize in `MiroFish/backend/app/services/`:
- `graph_builder.py`
- `ontology_generator.py`
- `oasis_profile_generator.py`
- `simulation_config_generator.py`
- `report_agent.py`

### Phase 4: Validation loop
Compare simulated outcomes against real historical aggregates.

Validate on metrics such as:
- failure rate by feature
- retry rate by segment
- support follow-up within 24h and 72h
- unresolved issue rate
- branch visit share after friction
- churn proxy movement

If simulated distributions drift too far from actual observed patterns, recalibrate persona rules and transition weights.

## Technical architecture recommendation

### DataForce side
Add a new pipeline module, for example:
- `mirofish_export_pipeline.py`

Responsibilities:
- load cleaned datasets
- reuse `friction_score_pipeline.py`
- derive customer persona attributes
- output JSON and Markdown seed files

Possible helper modules:
- `persona_builder.py`
- `journey_archetypes.py`
- `simulation_seed_writer.py`

### MiroFish side
Treat DataForce exports as seed documents and structured context for graph + simulation generation.

Recommended integration patterns:
1. **Document upload pattern**: export Markdown reports and JSON summaries, then upload them as seed materials.
2. **Direct backend ingestion pattern**: add a custom importer in the backend to ingest the generated JSON artifacts.
3. **Hybrid pattern**: use Markdown for narrative context and JSON for structured agent/profile injection.

The hybrid pattern is recommended.

## Suggested minimum viable integration
For a hackathon-friendly version, keep scope small and measurable.

### MVP objective
Simulate the probability that a customer who experiences a high-friction digital session will:
- retry successfully
- contact support
- abandon

### MVP data inputs
- `customers.csv`
- `digital_sessions.csv`
- `support_interactions.csv`
- `error_codes.csv`
- `feature_costs.csv`
- output of `friction_score_pipeline.py`

### MVP outputs
- 3 to 5 customer personas
- 3 scenario templates
- simulated outcome distribution per scenario
- report comparing intervention strategies

### Recommended MVP personas
- digitally savvy retail customer
- novice retail customer
- smb operator with urgent transfer need
- wealth customer with low failure tolerance
- student mobile-first customer

## Example simulation questions to answer
- If a `Student` user gets `AUTH_FAIL` during login, what is the likelihood they retry versus seek help?
- If an `SMB` user encounters transfer failure twice within 24 hours, how often does support escalation occur?
- Which intervention reduces mobile deposit support calls the most: tooltip, tutorial, or chatbot?
- Which features create the highest simulated support cost when failure premiums are considered?
- How much could proactive intervention reduce 24-hour support follow-up for high-friction sessions?

## Metrics to track

### Customer behavior metrics
- success rate
- retry rate
- abandonment rate
- support escalation rate
- time-to-resolution proxy
- simulated trust score

### Business metrics
- support cost avoided
- branch deflection rate
- unresolved issue reduction
- friction score reduction
- churn-risk proxy reduction

### Simulation quality metrics
- realism versus observed historical distributions
- stability across repeated runs
- sensitivity to intervention strategies
- explainability of agent outcomes

## Risks and mitigations

### Risk: digital sessions file is large and messy
Mitigation:
- preprocess into compact aggregates before importing to MiroFish
- sample representative journeys for early experiments

### Risk: MiroFish is optimized for rich narrative/world simulations, not tabular banking data
Mitigation:
- convert tabular data into structured personas, journey summaries, and scenario documents
- avoid trying to ingest raw CSV directly into simulation prompts

### Risk: overfitting simulation behavior to rules
Mitigation:
- validate against holdout aggregates
- keep persona generation interpretable
- compare simulated and real transition frequencies

### Risk: missing ground-truth churn outcomes beyond `churn_flag`
Mitigation:
- use churn as a proxy metric only
- prioritize support escalation and retry behavior for validation

## Recommended next steps
1. confirm the exact schema and size of `digital_sessions.csv`
2. run `friction_score_pipeline.py` to generate a scored session dataset
3. create a `mirofish_export_pipeline.py` file in the root project
4. generate persona and journey artifacts from the cleaned data
5. define 3 to 5 banking scenario prompts for MiroFish
6. wire exported artifacts into MiroFish graph building and simulation config generation
7. compare simulated outcomes against historical support follow-up rates
8. iterate on persona and intervention rules

## Deliverables checklist
- [ ] customer persona schema
- [ ] journey archetype definitions
- [ ] MiroFish export pipeline
- [ ] scenario pack documents
- [ ] validation dashboard/report
- [ ] intervention experiment summary

## Recommended file placement
Save this plan as:
- `mirofish_integration_plan.md`

Future implementation artifacts could live under:
- `artifacts/`
- `simulation_configs/`
- `docs/mirofish/`

## Bottom line
The strongest integration path is to use `DataForce` as the structured analytics and feature-engineering layer, then use `MiroFish` as the scenario simulation and decision-testing layer. Start by converting raw customer and session data into grounded personas, friction-aware journey archetypes, and intervention scenarios rather than feeding raw CSVs directly into the simulator.

## Current implementation status

The customer-simulation path has started and is now partially implemented.

### Completed now
- `mirofish_export_pipeline.py` can export `customer_personas.json` from `customers.csv` with `--customers-only`.
- `artifacts/customer_personas.json` has been generated successfully.
- `MiroFish` project import support now exists for customer persona artifacts.
- `MiroFish` can generate OASIS-compatible profiles directly from imported customer personas.
- `pages/Customer_Simulations.py` provides a working Streamlit simulation page based on customer personas and lightweight scenario controls.
- `MiroFish/.env` has been aligned to an OpenRouter OpenAI-compatible configuration pattern.

### Not completed yet
- banking-specific ontology generation from personas and journeys
- session-history-driven customer transitions
- support-agent and intervention-agent simulation inside full MiroFish runtime
- full backend-triggered banking simulation run from DataForce UI
- simulation validation against historical outcomes

## Customer simulation implementation plan - next phase

This section defines the next concrete implementation steps from the current customers-only baseline into a real MiroFish-backed customer simulation system.

### Phase A - stabilize the customers-only MVP

Goal: make the current customer simulation path reliable and demo-ready.

#### Tasks
1. add a direct button or action in `pages/Customer_Simulations.py` to confirm whether `customer_personas.json` exists and is fresh
2. add a sidebar option to regenerate customer personas from `customers.csv`
3. surface the top persona attributes in the UI:
	- segment
	- digital experience
	- support-seeking tendency
	- trust in digital banking
4. add export buttons for:
	- filtered personas
	- simulation results
5. add a simple scenario summary block that explains why the simulated outcome changed based on the selected intervention

#### Success criteria
- a user can open `Customer Simulation`
- confirm personas are loaded
- run a scenario without backend dependencies
- inspect and download the simulation result table

### Phase B - connect DataForce UI to MiroFish backend project creation

Goal: move from local-only preview to actual MiroFish project lifecycle usage.

#### Tasks
1. add a lightweight client function in DataForce to call:
	- `POST /project/create-from-personas`
2. add UI controls on `Customer Simulation` for:
	- project name
	- simulation requirement text
	- backend base URL
3. call the MiroFish endpoint and save the returned:
	- `project_id`
	- `persona_count`
	- project summary
4. display the project import status directly in Streamlit

#### Success criteria
- a user can create a MiroFish project from the personas without leaving the DataForce app
- the returned `project_id` is visible and reusable

### Phase C - generate MiroFish agent profiles from imported personas

Goal: convert customer personas into agent profiles suitable for actual MiroFish simulation.

#### Tasks
1. add a DataForce-side action to call:
	- `POST /generate-profiles-from-personas`
2. let the user choose output platform:
	- reddit
	- twitter
	- raw
3. show a preview table of generated agent profiles in Streamlit
4. persist the returned profile JSON under a local artifact path such as:
	- `artifacts/generated_oasis_profiles.json`

#### Success criteria
- the customer personas are transformed into OASIS-compatible profiles through the live MiroFish backend
- generated profiles are visible in the UI

### Phase D - add banking-specific simulation configuration

Goal: stop treating the simulation as generic social simulation and start modeling banking journeys explicitly.

#### New simulation entities to define
- customer
- digital feature
- support channel
- friction event
- intervention
- branch

#### New banking-specific state variables
- current feature intent
- friction score band
- retry propensity
- support escalation propensity
- trust score
- churn-risk proxy

#### Tasks
1. create a banking simulation config schema in DataForce or MiroFish
2. define scenario templates such as:
	- login failure recovery
	- transfer failure escalation
	- mobile deposit guidance success
	- unresolved issue to churn-risk path
3. create a JSON config artifact such as:
	- `artifacts/banking_simulation_config.json`
4. add support for intervention selection and simulation rounds

#### Success criteria
- a scenario is represented as structured config rather than only UI form inputs
- the same scenario can be replayed with different intervention settings

### Phase E - incorporate session history and support behavior

Goal: improve realism by grounding customer actions in observed session and support history.

#### Data inputs to add next
- `digital_sessions.csv`
- `support_interactions.csv`
- `error_codes.csv`
- `feature_costs.csv`

#### Tasks
1. optimize `friction_score_pipeline.py` so the full pipeline completes on the large session file
2. export:
	- `session_journeys.json`
	- `support_patterns.json`
	- `error_taxonomy.json`
	- `feature_risk_lookup.json`
3. connect these artifacts to the simulation state machine
4. make customer personas dynamic instead of static by adding:
	- retry history
	- support follow-up tendency
	- recent friction level

#### Success criteria
- customer decisions in simulation are influenced by real behavioral history
- simulation outcomes are more realistic than customers-only inference

### Phase F - full MiroFish-backed execution path

Goal: run real customer simulations through MiroFish services instead of only the local Mesa preview.

#### Tasks
1. add a DataForce page action to:
	- create/import project
	- generate profiles
	- create config
	- start simulation
2. expose result polling or result retrieval from the MiroFish backend
3. store returned simulation outputs locally under `artifacts/` for downstream dashboarding
4. show simulation results inside `Customer Simulation` with:
	- outcome distribution
	- cost impact
	- support escalation estimate
	- intervention comparison

#### Success criteria
- the Streamlit page can launch and review a real MiroFish simulation
- results flow back into DataForce visualizations

## Recommended immediate coding order

To keep momentum and avoid overbuilding, implement in this order:

1. enhance `pages/Customer_Simulations.py` with persona management and download actions
2. add a simple MiroFish backend connector in the Streamlit page
3. support project creation from persona artifact
4. support profile generation from personas
5. define one banking scenario config JSON
6. run one end-to-end backend-backed scenario
7. only then optimize the full session pipeline for historical grounding

## Immediate next deliverables

- [ ] persona regeneration control in `Customer Simulation`
- [ ] MiroFish backend URL + project creation form in Streamlit
- [ ] profile generation button using imported personas
- [ ] local save of generated OASIS profiles
- [ ] first banking scenario config file
- [ ] end-to-end demo path: personas → project → profiles → simulation request
