import streamlit as st
import os
from pathlib import Path
from PIL import Image

from app.services.user_service import (
    get_user_by_username,
    update_user_profile_image,
    remove_user_profile_image,
    get_valid_avatar_path,
)
from app.ui.styles import load_custom_css


class ProfilePage:
    IMAGE_FOLDER = "app/user_images"

    def __init__(self):
        load_custom_css()
        self.qp = st.query_params

        if "user" not in self.qp or not self.qp.get("user"):
            st.query_params.clear()
            st.switch_page("Home.py")
            st.stop()

        self.username = self.qp.get("user")[0]
        self.user = get_user_by_username(self.username)

        if not self.user:
            st.error("User not found.")
            st.stop()

        Path(self.IMAGE_FOLDER).mkdir(parents=True, exist_ok=True)

    def render(self):
        st.title("⚙️ Profile Settings")
        self.render_back_button()
        self.render_header()
        self.render_avatar_section()
        self.upload_avatar()

    def render_back_button(self):
        last = st.session_state.get("last_page")
        if last and st.button("⬅ Back"):
            st.switch_page(last)
        elif st.button("⬅ Back to Home"):
            st.switch_page("Home.py")
        
        # Remove profile picture button (only show if user has a profile picture)
        if self.user.get("avatar"):
            if st.button("🗑️ Remove Profile Picture", key="remove_avatar"):
                success, message = remove_user_profile_image(self.username)
                if success:
                    st.success(message)
                    st.cache_data.clear()
                    # Refresh user data
                    self.user = get_user_by_username(self.username)
                    st.rerun()
                else:
                    st.error(message)

        st.markdown("---")

    def render_header(self):
        colA, colB = st.columns([1, 3])

        with colA:
            self.render_avatar(size=120)

        with colB:
            st.markdown(
                f"<div style='font-size:24px;font-weight:700;color:white'>{self.username}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='color:#FF1493;font-size:12px;text-transform:uppercase'>{self.user['role']}</div>",
                unsafe_allow_html=True,
            )

            if st.button("Logout"):
                st.query_params.clear()
                st.switch_page("Home.py")

        st.markdown("---")

    def render_avatar(self, size=200):
        avatar = self.user.get("avatar")
        avatar_path = get_valid_avatar_path(self.username, avatar)
        
        if avatar_path and os.path.exists(avatar_path):
            st.image(avatar_path, width=size)
            st.markdown(
                "<style>img{border-radius:100%;border:3px solid #FF1493;}</style>",
                unsafe_allow_html=True,
            )
        else:
            st.info("No profile picture yet.")

    def render_avatar_section(self):
        st.markdown("### Current profile picture")
        self.render_avatar()

    def upload_avatar(self):
        st.markdown("### Upload a new profile picture")
        uploaded = st.file_uploader(
            "Choose an image", type=["png", "jpg", "jpeg"])

        if uploaded:
            self.save_avatar(uploaded)

    def save_avatar(self, uploaded):
        try:
            img = Image.open(uploaded).convert("RGB")
            save_path = os.path.abspath(
                os.path.join(self.IMAGE_FOLDER, f"{self.username}.jpg")
            ).replace("\\", "/")

            img.save(save_path, format="JPEG", quality=85)

            if update_user_profile_image(self.username, save_path):
                st.success("Avatar updated.")
                st.cache_data.clear()
                st.markdown(
                    "<script>window.location.reload();</script>",
                    unsafe_allow_html=True,
                )
                st.stop()
            else:
                st.error("Failed to update avatar.")

        except Exception as e:
            st.error(str(e))


# Entry point
ProfilePage().render()
