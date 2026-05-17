# Visual Test Selectors - <slug>

## Inputs

| Field | Value |
|---|---|
| Route or screen | <route_or_screen> |
| Source IDs | <interface-design/test-plan ids> |
| Owner | <owner> |

## Selector / State Recipes

| Route / Screen | State | Stable Selectors | Auth / Session Reference (no secrets) | Seed Data | Route Preconditions | Loading Completion / Ready State | Reduced Motion / Animation Control | Known Flaky States | Owner |
|---|---|---|---|---|---|---|---|---|---|
| <route> | <state> | role=<role>, label=<label>, test-id=<test-id> | <session> | <seed> | <preconditions> | <ready assertion> | <control> | <flaky notes> | <owner> |

Record only setup steps, fixture names, or redacted auth-state paths. Do not
paste tokens, cookies, auth-state blobs, passwords, or secret-bearing session
values.

## Rejected Brittle Selectors

| Selector | Reason Rejected | Replacement |
|---|---|---|
| <css/xpath/text> | <why brittle> | <stable selector> |

## Open Selector Risks

- <risk or none>
