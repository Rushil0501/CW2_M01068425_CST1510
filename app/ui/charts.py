import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

NEON_COLORS = ["#FF1493", "#00F0FF",
               "#FFD700", "#ADFF2F", "#FF4500", "#9400D3"]


def render_chart(df, chart_type="bar", x=None, y=None, color=None, title="", values=None, groupby=None):
    if df is None or df.empty:
        st.info("No data available for charts.")
        return

    if chart_type == "bar":
        if y is None and x is not None:
            # Count occurrences if y not provided
            value_counts = df[x].value_counts()
            fig = px.bar(
                x=value_counts.index, y=value_counts.values,
                title=title,
                template="plotly_dark",
                color_discrete_sequence=NEON_COLORS
            )
        else:
            fig = px.bar(
                df, x=x, y=y, color=color,
                title=title,
                template="plotly_dark",
                color_discrete_sequence=NEON_COLORS
            )

    elif chart_type == "pie":
        if values is not None:
            fig = px.pie(
                df, names=x, values=values,
                title=title,
                hole=0.5,
                color_discrete_sequence=NEON_COLORS
            )
        else:
            fig = px.pie(
                df, names=x,
                title=title,
                hole=0.5,
                color_discrete_sequence=NEON_COLORS
            )

    elif chart_type == "line":
        fig = px.line(
            df, x=x, y=y, color=color,
            markers=True,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=NEON_COLORS
        )
        fig.update_traces(line_shape="spline")   # Smooth curve

    elif chart_type == "scatter":
        scatter_kwargs = {
            "x": x,
            "y": y,
            "color": color,
            "title": title,
            "template": "plotly_dark",
            "color_discrete_sequence": NEON_COLORS
        }
        if y:
            scatter_kwargs["size"] = y
        fig = px.scatter(df, **scatter_kwargs)

    elif chart_type == "histogram":
        fig = px.histogram(
            df, x=x, color=color,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=NEON_COLORS,
            nbins=20
        )

    elif chart_type == "box":
        fig = px.box(
            df, x=x, y=y, color=color,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=NEON_COLORS
        )

    elif chart_type == "heatmap":
        if groupby and len(groupby) == 2:
            pivot_data = df.groupby(groupby).size().reset_index(name='count')
            pivot_table = pivot_data.pivot(index=groupby[0], columns=groupby[1], values='count').fillna(0)
            fig = px.imshow(
                pivot_table,
                title=title,
                template="plotly_dark",
                color_continuous_scale="Magma"
            )
        else:
            st.error("Heatmap requires groupby parameter with 2 columns.")
            return

    elif chart_type == "area":
        fig = px.area(
            df, x=x, y=y, color=color,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=NEON_COLORS
        )

    elif chart_type == "violin":
        fig = px.violin(
            df, x=x, y=y, color=color,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=NEON_COLORS
        )

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
