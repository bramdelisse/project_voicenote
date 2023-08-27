### TO DO

    [] Host a webapp on the Raspberry Pi
    [] Connect my code on the server side
    [] Make it all safe


### Code logic
- There are two github repositories. One public (server side), and one private (client).
    - The private repository works with environment variables such that the keys cannot become public.


### Schematic overview

```mermaid
flowchart LR
    N[(Notion)]
    S{Server}
    O{OpenAI}
    P[Phone]

    P -- Voice message --> S
    S <-- Transcribe & Summarize--> O
    S --> N