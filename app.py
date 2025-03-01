# app.py
import pandas as pd
import streamlit as st
from PIL import Image
import plotly.graph_objects as go
import flagpy as fp
import requests
from io import BytesIO
from pathlib import Path

from FMSCOUT.data_manager import DataManager
from FMSCOUT.similarity_calculator import SimilarityCalculator


class PlayerRecommendationAPP:
    def __init__(self):
        self.data_manager = DataManager()
        self.sim_calc = SimilarityCalculator()
        self.setup_streamlit()

    @staticmethod
    def setup_streamlit():
        # 페이지 배경 및 스타일 설정
        page_bg_img = """
                <style>
                [data-testid="stAppViewContainer"]{
                  background-image: url('''https://images.unsplash.com/photo-1431324155629
                  -1a6deb1dec8d?ixlib=rb-4.0.3&ixid=
                  M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1740&q=80''');
                  background-size: cover;
                }
                [data-testid="stHeader"]{
                  background-color: rgba(0,0,0,0);
                }
                [data-testid="stToolbar"]{
                  right: 2rem;
                  background-color: #42F328;
                }
                </style>
                """
        st.markdown(page_bg_img, unsafe_allow_html=True)
        st.markdown("""
                <style>
                [data-testid="stSidebar"]{
                  background-color: #0F0F0F;
                  color: #42F328;
                }
                [data-testid="stMarkdownContainer"] > div > h2{
                  color: white;
                }
                [data-testid="stMarkdownContainer"] > p{
                  color: white;
                }
                </style>
                """, unsafe_allow_html=True)
        st.markdown("""
                <style>
                [data-testid="stMetricValue"]{
                  color: #42F328;
                  font-size: 40px;
                }
                [data-testid="stMarkdownContainer"] > div > h3 > div > span{
                  color: white;
                }
                </style>
                """, unsafe_allow_html=True)

    def run(self):
        st.sidebar.header("당신의 유망주를 찾아드립니다")
        player_names = self.data_manager.get_all_player_names()
        player_input = st.sidebar.selectbox('게임 내 좋아하는 선수를 입력하세요: ', player_names, index=7755)
        threshold_input = st.sidebar.number_input('최대 나이를 입력해주세요 (~ 25): ', 0, 99)
        base_dir = Path(__file__).resolve().parent.parent
        fm_image = base_dir / "data" / 'scouter_image2.png'

        st.sidebar.image(str(fm_image))

        if not player_input:
            st.write("선수를 선택해 주세요")
            return

        try:
            temp_df, temp_df_scl, categories, skill_calculator = self.data_manager.get_player_data(player_input)
        except ValueError as e:
            st.error(str(e))
            return

        cluster = temp_df_scl[temp_df_scl['Name'] == player_input]['cluster']
        input_df = temp_df[temp_df['Name'] == player_input]
        cl_df = temp_df_scl[temp_df_scl['cluster'].apply(lambda x: any(k in x for k in cluster.values[0]))].reset_index(
            drop=True)
        original_df = temp_df[temp_df['cluster'].apply(lambda x: any(k in x for k in cluster.values[0]))].reset_index(
            drop=True)

        try:
            player_index = cl_df[cl_df['Name'] == player_input].index[0]
        except IndexError:
            st.error("선수 데이터를 찾을 수 없습니다.")
            return

        cl_x = cl_df.iloc[:, 1:-1].values
        vectors = {i: x.tolist() for i, x in enumerate(cl_x)}

        if threshold_input == 0:
            st.error("최대 나이를 0보다 크게 입력하세요.")
            return

        top_sim_players = self.sim_calc.similar_players(vectors, player_index)
        top_players = {}
        for index, similarity in top_sim_players.items():
            info = list(original_df.iloc[index].values)
            info.insert(1, similarity)
            top_players[index] = info

        cols = list(original_df.columns)
        cols.insert(1, 'similarity')
        output = pd.DataFrame.from_dict(data=top_players, orient='index', columns=cols)
        filtered_output = output[output['Age'] <= threshold_input]

        filtered_output['similarity'] = filtered_output['similarity'].apply(lambda x: round(x, 2))

        st.write("가장 플레이스타일이 비슷한 유망주는....")
        filtered_output = filtered_output.sort_values(by=['similarity', 'pa'], ascending=False)
        first_similar_player = filtered_output.iloc[0]
        col1, col2, col3 = st.columns(3)
        col2.header(first_similar_player['Name'])

        # Radar Chart
        famous = input_df.iloc[0]
        youth = filtered_output.iloc[0]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=skill_calculator.calculate(famous),
            theta=categories,
            fill='toself',
            name=f'{player_input}'
        ))
        fig.add_trace(go.Scatterpolar(
            r=skill_calculator.calculate(youth),
            theta=categories,
            fill='toself',
            opacity=0.6,
            marker_color='green',
            fillcolor='#42F328',
            name=f"{first_similar_player['Name']}"
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 20])),
                          plot_bgcolor='rgba(0,0,0,0)',
                          paper_bgcolor='rgba(0,0,0,0)',
                          showlegend=False)

        # 추천 이미지 로드
        pics_row = original_df.loc[original_df['Name'] == first_similar_player['Name']]
        # 기본 이미지 URL 설정
        default_image_url = "https://static.vecteezy.com/system/resources/thumbnails/020/765/399/small_2x/default-profile-account-unknown-icon-black-silhouette-free-vector.jpg"
        pics_row['pics'] = pics_row['pics'].replace(float('nan'), default_image_url)
        image_address = pics_row['pics'].values[0]
        response = requests.get(image_address)
        img = Image.open(BytesIO(response.content))
        with col2:
            st.image(img)
        with col3:
            st.metric(label="유사도", value=f"{first_similar_player['similarity'] * 100}%")

        col2.subheader('나이: ' + str(first_similar_player['Age']))
        col2.subheader('포지션: ' + str(first_similar_player['Position']))
        col2.subheader('국적')
        flag_list = []
        try:
            for nat in first_similar_player['Nationality'].split(','):
                flag_list.append(fp.get_flag_img(nat.strip()))
            col2.image(flag_list, width=100)
        except:
            col2.subheader(first_similar_player['Nationality'])
        col2.subheader('클럽: ' + str(first_similar_player['Club']))

        st.plotly_chart(fig)

        # Recommendation Video
        video_row = original_df.loc[original_df['Name'] == first_similar_player['Name']]
        try:
            video_address = video_row['video'].values[0]
            st.video(video_address, format='video/mp4', start_time=0)
        except:
            col2.subheader('Search on Youtube')

        # Similar Player list
        temp = filtered_output[['Name', 'similarity', 'Position', 'Age', 'Nationality', 'Club']]
        temp['similarity'] = temp['similarity'].apply(lambda x: f"{x * 100}%")
        if len(filtered_output) == 1:
            st.write('그 외 유사선수가 존재하지 않습니다.')
        else:
            st.write('그 외 유사 선수목록')
            limit_num = len(temp)
            if len(temp) > 6:
                limit_num = 6
            st.table(
                temp.iloc[1:limit_num]
                .style
                .set_properties(**{'border': ' 1.5px solid #42F328', 'color': '#42F328'})
                .hide(axis="index")
            )


def main():
    app = PlayerRecommendationAPP()
    app.run()


if __name__ == '__main__':
    main()
