from __future__ import annotations

from services.mock_data import Role, Ticket


def build_starter_message(ticket: Ticket, current_role: Role) -> str:
    if current_role == "Business Analyst":
        return (
            f"I am ready to collaborate on **{ticket['subject']}** as a "
            f"**{current_role}**.\n\n"
            "- I can help clarify business goals, stakeholder expectations, and user impact.\n"
            "- We can turn rough notes into requirements, acceptance criteria, and follow-up questions.\n"
            "- Ask what is still unclear, what decision is needed, or what update should go back to the team."
        )

    return (
        f"I am ready to collaborate on **{ticket['subject']}** as a "
        f"**{current_role}**.\n\n"
        "- I can help break the ticket into implementation steps, APIs, and likely code touchpoints.\n"
        "- We can walk through edge cases, testing ideas, rollout concerns, and technical unknowns.\n"
        "- Ask about debugging paths, system behavior, or what needs to change in code."
    )


def build_mock_agent_reply(ticket: Ticket, current_role: Role, prompt: str) -> str:
    cleaned_prompt = prompt.strip()

    if not cleaned_prompt:
        return (
            f"I am ready to help with **{ticket['subject']}** from the "
            f"**{current_role}** perspective."
        )

    if current_role == "Business Analyst":
        return (
            f"Working on **{ticket['subject']}** as a **{current_role}**.\n\n"
            f"- Business view of your message: {cleaned_prompt}\n"
            "- Likely focus areas: requirement clarity, user impact, stakeholder alignment, and decision points.\n"
            f"- Suggested next step: capture the open question for ticket `{ticket['id']}` and confirm what outcome the business needs before implementation starts."
        )

    return (
        f"Working on **{ticket['subject']}** as a **{current_role}**.\n\n"
        f"- Technical view of your message: {cleaned_prompt}\n"
        "- Likely focus areas: implementation steps, APIs or integrations, edge cases, and validation.\n"
        f"- Suggested next step: inspect the systems behind ticket `{ticket['id']}`, identify the code path, and define the tests needed before rollout."
    )


def build_assistant_status(ticket: Ticket, current_role: Role) -> tuple[str, str]:
    if current_role == "Business Analyst":
        return (
            "Ready for requirement clarification",
            f"Focused on business impact, acceptance criteria, and stakeholder questions for {ticket['id']}.",
        )

    return (
        "Ready for implementation discussion",
        f"Focused on code paths, APIs, testing, and rollout risk for {ticket['id']}.",
    )


def build_chat_input_placeholder(current_role: Role) -> str:
    if current_role == "Business Analyst":
        return "Ask how this ticket affects business requirements..."

    return "Ask about implementation, APIs, tests, or code changes..."
