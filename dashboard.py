
# ============================================================
#  BEMM461 Coursework 2 — Interactive Dashboard
#  Topic: Visual Platforms & Wellbeing
#  Tool: Plotly Dash (runs in your browser)
# ============================================================
#
#  HOW TO RUN:
#  1. Open Terminal (Mac) or Command Prompt (Windows)
#  2. Navigate to the folder where this file is saved:
#       cd path/to/your/folder
#  3. Run: python dashboard.py
#  4. Open your browser and go to: http://127.0.0.1:8050
#  5. Take screenshots of the dashboard for your report!
#
#  IMPORTANT: Make sure these 3 CSV files are in the SAME
#  folder as this dashboard.py file:
#    - instagram_clean.csv
#    - anxiety_gender_dashboard.csv
#    - anxiety_age_dashboard.csv
# ============================================================

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Load Data ────────────────────────────────────────────────
insta = pd.read_csv('instagram_clean.csv')
anxiety_gender = pd.read_csv('anxiety_gender_dashboard.csv')
anxiety_age = pd.read_csv('anxiety_age_dashboard.csv')

# Create follower segments if not already present
if 'Follower_Segment' not in insta.columns:
    insta['Follower_Segment'] = pd.cut(
        insta['Number of Followers'],
        bins=[0, 500, 2000, 10000, 999999],
        labels=['Micro (<500)', 'Small (500-2K)', 'Medium (2K-10K)', 'Large (10K+)']
    )

# ── Colour Palette (consistent across all charts) ────────────
FEMALE_COLOR = '#E87C9A'   # Pink for Female
MALE_COLOR   = '#5B9BD5'   # Blue for Male
BG_COLOR     = '#F8F9FA'   # Light grey background
CARD_COLOR   = '#FFFFFF'   # White card background
TEXT_COLOR   = '#2D3436'   # Dark text
ACCENT_COLOR = '#6C5CE7'   # Purple accent for age chart

# Shortened age labels for the chart axis
AGE_LABELS = {
    '18 - 29 years': '18-29',
    '30 - 39 years': '30-39',
    '40 - 49 years': '40-49',
    '50 - 59 years': '50-59',
    '60 - 69 years': '60-69',
    '70 - 79 years': '70-79',
    '80 years and above': '80+'
}
anxiety_age['Age Label'] = anxiety_age['Subgroup'].map(AGE_LABELS)

# ── App Initialisation ───────────────────────────────────────
app = dash.Dash(__name__)
app.title = "Visual Platforms & Wellbeing Dashboard"

# ── Layout ───────────────────────────────────────────────────
# The layout is like an HTML page — built with nested boxes.
# We use a card-style design so each section feels distinct.
app.layout = html.Div(style={
    'backgroundColor': BG_COLOR,
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'minHeight': '100vh',
    'padding': '0'
}, children=[

    # ── Header Banner ────────────────────────────────────────
    html.Div(style={
        'background': 'linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%)',
        'padding': '24px 40px',
        'color': 'white',
        'marginBottom': '24px'
    }, children=[
        html.H1("Visual Platforms & Wellbeing",
                style={'margin': '0', 'fontSize': '26px', 'fontWeight': '700'}),
        html.P("Exploring the relationship between Instagram behaviour and mental health indicators",
               style={'margin': '6px 0 0 0', 'fontSize': '14px', 'opacity': '0.9'}),
    ]),

    # ── Main Content Area ─────────────────────────────────────
    html.Div(style={'padding': '0 32px 32px 32px'}, children=[

        # ── Filter Panel (top row) ────────────────────────────
        # Filters sit at the top so users see them before the charts.
        # This follows dashboard UX best practice — controls before content.
        html.Div(style={
            'backgroundColor': CARD_COLOR,
            'borderRadius': '12px',
            'padding': '20px 28px',
            'marginBottom': '24px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
            'display': 'flex',
            'gap': '48px',
            'alignItems': 'center',
            'flexWrap': 'wrap'
        }, children=[
            html.Div([
                html.Label("🔍  Filter by Gender",
                           style={'fontWeight': '600', 'fontSize': '13px',
                                  'color': TEXT_COLOR, 'marginBottom': '8px', 'display': 'block'}),
                dcc.Checklist(
                    id='gender-filter',
                    options=[{'label': '  Female', 'value': 'Female'},
                             {'label': '  Male',   'value': 'Male'}],
                    value=['Female', 'Male'],   # both selected by default
                    inline=True,
                    inputStyle={'marginRight': '4px', 'cursor': 'pointer'},
                    labelStyle={'marginRight': '20px', 'fontSize': '14px', 'cursor': 'pointer'}
                )
            ]),

            html.Div([
                html.Label("📊  Filter by Follower Segment",
                           style={'fontWeight': '600', 'fontSize': '13px',
                                  'color': TEXT_COLOR, 'marginBottom': '8px', 'display': 'block'}),
                dcc.Checklist(
                    id='segment-filter',
                    options=[
                        {'label': '  Micro (<500)',    'value': 'Micro (<500)'},
                        {'label': '  Small (500-2K)',  'value': 'Small (500-2K)'},
                        {'label': '  Medium (2K-10K)', 'value': 'Medium (2K-10K)'},
                    ],
                    value=['Micro (<500)', 'Small (500-2K)', 'Medium (2K-10K)'],
                    inline=True,
                    inputStyle={'marginRight': '4px', 'cursor': 'pointer'},
                    labelStyle={'marginRight': '20px', 'fontSize': '14px', 'cursor': 'pointer'}
                )
            ]),

            # Live stats update as filters change — shows user count
            html.Div(id='stats-display', style={
                'marginLeft': 'auto',
                'backgroundColor': '#f0edff',
                'borderRadius': '8px',
                'padding': '10px 18px',
                'fontSize': '13px',
                'color': '#6C5CE7',
                'fontWeight': '600'
            })
        ]),

        # ── Chart Row 1: Scatter + Bar ────────────────────────
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr',
                        'gap': '24px', 'marginBottom': '24px'}, children=[

            # Scatter Plot card
            html.Div(style={
                'backgroundColor': CARD_COLOR, 'borderRadius': '12px',
                'padding': '20px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'
            }, children=[
                html.H3("Engagement Rate vs Self-Presentation",
                        style={'margin': '0 0 4px 0', 'fontSize': '15px',
                               'fontWeight': '700', 'color': TEXT_COLOR}),
                html.P("Each dot = one Instagram user | Colour = Gender | Size = Followers",
                       style={'margin': '0 0 12px 0', 'fontSize': '11px', 'color': '#888'}),
                dcc.Graph(id='scatter-chart', config={'displayModeBar': False})
            ]),

            # Mental Health by Gender bar chart card
            html.Div(style={
                'backgroundColor': CARD_COLOR, 'borderRadius': '12px',
                'padding': '20px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'
            }, children=[
                html.H3("Mental Health Indicators by Gender",
                        style={'margin': '0 0 4px 0', 'fontSize': '15px',
                               'fontWeight': '700', 'color': TEXT_COLOR}),
                html.P("Population-level survey data | % of population reporting symptoms",
                       style={'margin': '0 0 12px 0', 'fontSize': '11px', 'color': '#888'}),
                dcc.Graph(id='mental-health-gender-chart', config={'displayModeBar': False})
            ]),
        ]),

        # ── Chart Row 2: Age Line Chart (full width) ──────────
        html.Div(style={
            'backgroundColor': CARD_COLOR, 'borderRadius': '12px',
            'padding': '20px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
            'marginBottom': '24px'
        }, children=[
            html.H3("Mental Health Indicators Across Age Groups",
                    style={'margin': '0 0 4px 0', 'fontSize': '15px',
                           'fontWeight': '700', 'color': TEXT_COLOR}),
            html.P("18–29 age group highlighted — the core Instagram demographic with highest anxiety and depression rates",
                   style={'margin': '0 0 12px 0', 'fontSize': '11px', 'color': '#888'}),
            dcc.Graph(id='age-chart', config={'displayModeBar': False})
        ]),

        # ── Key Insight Summary Cards ─────────────────────────
        # These update dynamically based on the filtered data,
        # giving the user quick takeaways without reading charts.
        html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)',
                        'gap': '16px'}, children=[
            html.Div(id='insight-1', style={
                'backgroundColor': '#fff5f8', 'borderRadius': '10px',
                'padding': '16px 20px', 'borderLeft': f'4px solid {FEMALE_COLOR}'
            }),
            html.Div(id='insight-2', style={
                'backgroundColor': '#f0f7ff', 'borderRadius': '10px',
                'padding': '16px 20px', 'borderLeft': f'4px solid {MALE_COLOR}'
            }),
            html.Div(id='insight-3', style={
                'backgroundColor': '#f0edff', 'borderRadius': '10px',
                'padding': '16px 20px', 'borderLeft': f'4px solid {ACCENT_COLOR}'
            }),
        ]),

        # Footer
        html.Div(style={'textAlign': 'center', 'marginTop': '28px',
                        'fontSize': '11px', 'color': '#aaa'},
                 children="BEMM461 Coursework 2 — Visual Platforms & Wellbeing Dashboard")
    ])
])


# ── Callbacks (the "brain" that makes charts interactive) ────
# Every time a filter changes, Dash calls this function and
# re-renders all outputs simultaneously — this is what makes
# the dashboard "interconnected."
@app.callback(
    Output('scatter-chart', 'figure'),
    Output('mental-health-gender-chart', 'figure'),
    Output('age-chart', 'figure'),
    Output('stats-display', 'children'),
    Output('insight-1', 'children'),
    Output('insight-2', 'children'),
    Output('insight-3', 'children'),
    Input('gender-filter', 'value'),
    Input('segment-filter', 'value'),
)
def update_all_charts(selected_genders, selected_segments):
    # ── Filter Instagram data based on user selections ────────
    filtered = insta[
        (insta['Gender'].isin(selected_genders)) &
        (insta['Follower_Segment'].isin(selected_segments))
    ]

    # Guard against empty selections
    if filtered.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            annotations=[dict(text="No data matches current filters",
                              showarrow=False, font=dict(size=14))],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        no_data = html.P("No data", style={'color': '#aaa'})
        return empty_fig, empty_fig, empty_fig, "0 users", no_data, no_data, no_data

    # ── Chart 1: Scatter Plot ─────────────────────────────────
    scatter_fig = go.Figure()
    color_map = {'Female': FEMALE_COLOR, 'Male': MALE_COLOR}

    for gender in selected_genders:
        g_data = filtered[filtered['Gender'] == gender]
        scatter_fig.add_trace(go.Scatter(
            x=g_data['Engagement Rate (%)'],
            y=g_data['Self-Presentation Ratio (%)'],
            mode='markers',
            name=gender,
            marker=dict(
                color=color_map[gender],
                size=g_data['Number of Followers'] / 300 + 5,  # scale dot size by followers
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            hovertemplate=(
                f"<b>{gender}</b><br>"
                "Engagement Rate: %{x:.1f}%<br>"
                "Self-Presentation: %{y:.1f}%<br>"
                "Followers: %{customdata:,}<extra></extra>"
            ),
            customdata=g_data['Number of Followers']
        ))

    scatter_fig.update_layout(
        xaxis_title="Engagement Rate (%)",
        yaxis_title="Self-Presentation Ratio (%)",
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(248,249,250,0.5)',
        height=340,
        xaxis=dict(gridcolor='#eee', zeroline=False),
        yaxis=dict(gridcolor='#eee', zeroline=False),
        font=dict(family='Segoe UI, Arial', size=12)
    )

    # ── Chart 2: Mental Health by Gender Bar Chart ────────────
    # Filter mental health data to match selected genders
    mh_filtered = anxiety_gender[anxiety_gender['Subgroup'].isin(selected_genders)]

    short_names = {
        'Symptoms of Anxiety Disorder': 'Anxiety',
        'Symptoms of Depressive Disorder': 'Depression',
        'Symptoms of Anxiety Disorder or Depressive Disorder': 'Anxiety or\nDepression'
    }
    mh_filtered = mh_filtered.copy()
    mh_filtered['Short Indicator'] = mh_filtered['Indicator'].map(short_names)

    mh_fig = go.Figure()
    for gender in selected_genders:
        g_mh = mh_filtered[mh_filtered['Subgroup'] == gender]
        mh_fig.add_trace(go.Bar(
            x=g_mh['Short Indicator'],
            y=g_mh['Value'],
            name=gender,
            marker_color=color_map[gender],
            opacity=0.88,
            text=g_mh['Value'].apply(lambda v: f'{v:.1f}%'),
            textposition='outside',
        ))

    mh_fig.update_layout(
        barmode='group',
        yaxis_title="% of Population Affected",
        yaxis=dict(range=[0, 48], gridcolor='#eee', zeroline=False),
        xaxis=dict(gridcolor='#eee'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(248,249,250,0.5)',
        height=340,
        font=dict(family='Segoe UI, Arial', size=12)
    )

    # ── Chart 3: Age Line Chart ───────────────────────────────
    # This chart does not filter by gender/segment since it is
    # population-level data — but it updates to stay visually fresh.
    age_fig = go.Figure()

    indicator_styles = {
        'Symptoms of Anxiety Disorder':
            dict(color=FEMALE_COLOR, dash='solid', name='Anxiety Disorder'),
        'Symptoms of Depressive Disorder':
            dict(color=MALE_COLOR, dash='solid', name='Depressive Disorder'),
        'Symptoms of Anxiety Disorder or Depressive Disorder':
            dict(color=ACCENT_COLOR, dash='dot', name='Anxiety or Depression'),
    }

    for indicator, style in indicator_styles.items():
        ind_data = anxiety_age[anxiety_age['Indicator'] == indicator]
        age_fig.add_trace(go.Scatter(
            x=ind_data['Age Label'],
            y=ind_data['Value'],
            mode='lines+markers',
            name=style['name'],
            line=dict(color=style['color'], width=2.5, dash=style['dash']),
            marker=dict(size=8, color=style['color']),
            hovertemplate=f"<b>{style['name']}</b><br>Age: %{{x}}<br>Rate: %{{y:.1f}}%<extra></extra>"
        ))

    # Highlight 18-29 band as the core Instagram demographic
    age_fig.add_vrect(
        x0=-0.5, x1=0.5,
        fillcolor='rgba(232, 124, 154, 0.12)',
        layer='below', line_width=0,
        annotation_text="Core Instagram\nDemographic",
        annotation_position="top left",
        annotation_font=dict(size=10, color=FEMALE_COLOR)
    )

    age_fig.update_layout(
        xaxis_title="Age Group",
        yaxis_title="% of Population Affected",
        yaxis=dict(range=[0, 58], gridcolor='#eee', zeroline=False),
        xaxis=dict(gridcolor='#eee'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(248,249,250,0.5)',
        height=300,
        font=dict(family='Segoe UI, Arial', size=12)
    )

    # ── Dynamic Stats Display ─────────────────────────────────
    stats_text = f"Showing {len(filtered):,} of {len(insta):,} users"

    # ── Dynamic Insight Cards ─────────────────────────────────
    avg_engagement = filtered['Engagement Rate (%)'].mean()
    avg_self_pres  = filtered['Self-Presentation Ratio (%)'].mean()
    avg_followers  = filtered['Number of Followers'].mean()

    insight1 = [
        html.P("Avg Engagement Rate", style={'margin': '0', 'fontSize': '11px', 'color': '#888'}),
        html.H2(f"{avg_engagement:.1f}%", style={'margin': '4px 0', 'color': FEMALE_COLOR, 'fontSize': '28px'}),
        html.P("for selected users", style={'margin': '0', 'fontSize': '11px', 'color': '#aaa'})
    ]
    insight2 = [
        html.P("Avg Self-Presentation", style={'margin': '0', 'fontSize': '11px', 'color': '#888'}),
        html.H2(f"{avg_self_pres:.1f}%", style={'margin': '4px 0', 'color': MALE_COLOR, 'fontSize': '28px'}),
        html.P("of recent posts", style={'margin': '0', 'fontSize': '11px', 'color': '#aaa'})
    ]
    insight3 = [
        html.P("Avg Followers", style={'margin': '0', 'fontSize': '11px', 'color': '#888'}),
        html.H2(f"{avg_followers:,.0f}", style={'margin': '4px 0', 'color': ACCENT_COLOR, 'fontSize': '28px'}),
        html.P("per user (filtered)", style={'margin': '0', 'fontSize': '11px', 'color': '#aaa'})
    ]

    return scatter_fig, mh_fig, age_fig, stats_text, insight1, insight2, insight3


# ── Run the App ───────────────────────────────────────────────
if __name__ == '__main__':
    # debug=True means the app auto-reloads if you edit the code
    app.run(debug=True, port=8050)
