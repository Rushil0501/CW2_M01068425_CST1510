import streamlit as st
from app.services.user_service import get_user_by_username, get_valid_avatar_path


def render_dashboard_header(username: str, role: str):

    col_a, col_b, col_c = st.columns([1, 6, 2])

    with col_a:
        user_data = get_user_by_username(username)
        avatar = user_data.get("avatar") if user_data else None
        avatar_path = get_valid_avatar_path(username, avatar)

        if avatar_path:
            st.image(avatar_path, width=70)
            st.markdown(
                """
                <style>
                img {
                    border-radius: 50%;
                    border: 3px solid #FF1493;
                    box-shadow: 0 0 10px rgba(255,20,147,0.6);
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        else:
            initials = "".join([p[0].upper()
                               for p in username.split()][:2]) or "U"
            st.markdown(
                f"""
                <div style="width:70px; height:70px; border-radius:50%;
                            display:flex; align-items:center; justify-content:center;
                            background:#111; border:3px solid #FF1493;
                            color:white; font-weight:700; font-size:26px;
                            box-shadow:0 0 10px rgba(255,20,147,0.6);">
                    {initials}
                </div>
                """,
                unsafe_allow_html=True
            )

    with col_b:
        st.markdown(
            f"<div style='font-size:20px; font-weight:700; color:white'>{username}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='color:#FF1493; font-size:12px; text-transform:uppercase'>{role}</div>",
            unsafe_allow_html=True
        )

    with col_c:
        b1, b2 = st.columns([1, 1])
        with b1:
            if st.button("Profile"):
                st.switch_page("pages/profile.py")
        with b2:
            if st.button("Logout"):
                st.query_params.clear()
                st.switch_page("Home.py")

    st.markdown("---")
