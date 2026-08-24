## F1 - A database write never commits

**location:** the create-note route
**Consequences:** User will see a 201 but data will be silently missing
**How it should be:** The commit must be *Called* not referenced a transaction is only durable once it complete
**Severity:** not high

## F2 - Unbounded Read

**location:** The Get notes route
**Consequences:** Service can crash on huge amount of read
**How it should be:** Applying a limit on the read
**Severity:** High (as it can crash the service)

## F3 - Data leak

**location:** schema models
**Consequences:** Can expose data that should not be sent in a response
**How it should be:** Add only those variable in  response model that should be sent so any data other than that can be cutoff
**Severity:** High

## F4 - Mass assignment

**location:** schema models
**Consequences:** The client can set data that it should be able to
**How it should be:** Only set those variable in write schema model that the client can set
**Severity:** High

## F4 - No length constraint in Body

**location:** Http requests
**Consequences:** one request can fill memory and disk
**How it should be:** Set a limit of how much data can be sent
**Severity:** medium
