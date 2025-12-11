import streamlit as st
import plotly.express as px

NEON_COLORS = ["#FF1493", "#00F0FF",
               "#FFD700", "#ADFF2F", "#FF4500", "#9400D3"]


def render_chart(df, chart_type="bar", x=None, y=None, color=None, title=""):
    if df is None or df.empty:
        st.info("No data available for charts.")
        return

    if chart_type == "bar":
        fig = px.bar(
            df, x=x, y=y, color=color,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=NEON_COLORS
        )

    elif chart_type == "pie":
        fig = px.pie(
            df, names=x,
            title=title,
            hole=0.5,
            color_discrete_sequence=NEON_COLORS
        )

    elif chart_type == "line":
        fig = px.line(
            df, x=x, y=y,
            markers=True,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=NEON_COLORS
        )
        fig.update_traces(line_shape="spline")   # Smooth curve line

    else:
        st.error("Unknown chart type.")
        return

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E0E0E0"),
        title_font=dict(size=20, color="#FF1493")
    )

    st.plotly_chart(fig, width='stretch')
