global_style_string = '''
    <style>
        .block-container {
            margin-top: 0rem;
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }
        .reportview-container {
            margin-top: -2em;
        }
        header {
            visibility: hidden;
        }  
        div[data-test-scroll-behavior='scroll-to-bottom'] {
            height: 78.25vh;
        }
        .stCodeBlock {
            max-height: 300px;
            border-radius: 8px;
            width: 100%;
            overflow-x: hidden;
        }
        pre code {
            font-size: 0.9em;
            white-space: pre-wrap !important;
        }     
        iframe {
            width: 100%;
            border-radius: 8px;
        }
        .stChatMessage {
            cursor: pointer; 
            border: 1px solid transparent;
            transition: all 200ms ease-in-out;
        }
        .stChatMessage:hover {
            border: 1px solid #555555;
            transition: all 200ms ease-in-out;
        }
        .stChatMessage.selected {
            border: 1px solid #888888;
            transition: all 100ms ease-in-out;
        }
        div[data-testid='stHorizontalBlock']:nth-of-type(3) {
            flex-wrap: initial;
        }
        div[data-testid='stHorizontalBlock']:nth-of-type(3) > div[data-testid='column']:nth-of-type(1) {
            flex: 0 0 89px;
            min-width: 0px;
        }
        div[data-testid='stHorizontalBlock']:nth-of-type(3) > div[data-testid='column']:nth-of-type(2) {
            flex-shrink: 1;
            min-width: 0px;
        }
        iframe > div {
            border: 1px solid red;
        }
        row-widget stSelectbox {
            width: 50px;
            border: 1px solid red;
        }
    </style>
'''

# iframe:contains(div.legend) {
#             background: #ffffffbb;
#             border-radius: 0 0 8px 8px;
#             padding-bottom: 8px;
#             margin-right: -15px;
#         }