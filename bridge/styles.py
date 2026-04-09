from __future__ import annotations

SHARED_CSS = """
<style>
    /* Sidebar: only active nav item in red */
    [data-testid="stSidebarNavLink"][aria-current="page"] span,
    [data-testid="stSidebarNavLink"][aria-current="page"] a {
        color: #e30613 !important;
        font-weight: 700 !important;
    }
</style>
"""


def inject_shared_css() -> None:
    import streamlit as st
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
