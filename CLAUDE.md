This repo will contain an MCP server written in Python, to access the New Relic API.

The first step will be to PLAN what we do before making code. we will keep revising the plan.
The fundamental goal is simple code as possible.


The first New Relic feature we will do is to query logs.
I want to do this so claude can help investigate bugs we find in production, and then reason about the code that emits logs of that pattern.



The instructions below about the new relic API are making some assumptions about its capabilities. 
If there is a contradiction, please put that in the plan under 'issues to resolve'

Auth will be in the form of a personal API Key from New Relic (unless this contradicts their docs.)


Claude must be able to provide: 
1. arbitrary query parameters (like user_email:"someone@example.com")
2. a new relic account ID (or account name, and it can look up the account ID if that is possible)
3. Basic text search which new relic typically considers an attribute called 'message'






