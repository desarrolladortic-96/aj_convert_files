from dash import dcc, html
from dash.dependencies import Input, Output, State
from django_plotly_dash import DjangoDash
from PIL import Image
import io
import base64
import datetime
import torch
from diffusers import StableDiffusionPipeline

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def create_dash_app_generacion_imagenes():

    model_id = "stabilityai/stable-diffusion-2-1-base"

    # Load the Stable Diffusion model based on device availability
    if torch.cuda.is_available():
        device = "cuda"
        stable_diffusion_model = StableDiffusionPipeline.from_pretrained(
            model_id, revision="fp16", torch_dtype=torch.float16
        )
    else:
        device = "cpu"
        stable_diffusion_model = StableDiffusionPipeline.from_pretrained(
            model_id, torch_dtype=torch.float32
        )

    stable_diffusion_model.to(device)

    # Function to generate image using the Stable Diffusion model
    def generate_image(prompt_text, guidance_scale, num_inference_steps):
        try:
            if device == "cuda":
                with torch.autocast("cuda"):
                    result = stable_diffusion_model(
                        prompt_text, 
                        guidance_scale=guidance_scale, 
                        num_inference_steps=num_inference_steps
                    )
            else:
                result = stable_diffusion_model(
                    prompt_text, 
                    guidance_scale=guidance_scale, 
                    num_inference_steps=num_inference_steps
                )

            image = result.images[0]
            return image

        except Exception as e:
            print(f"Error generating the image: {e}")
            return None

    # Initialize Django Dash app
    app = DjangoDash('ImageApp', external_stylesheets=external_stylesheets)

    # Define layout of the app
    app.layout = html.Div([
        html.Div([
            dcc.Input(id='input-prompt', type='text', placeholder='Enter prompt', style={'width': '100%'}),
            dcc.Input(id='input-guidance-scale', type='number', placeholder='Guidance scale', value=7.5, style={'margin-top': '10px'}),
            dcc.Input(id='input-steps', type='number', placeholder='Inference steps', value=50, style={'margin-top': '10px'}),
        ]),
        html.Button('Generate Image', id='generate-btn', n_clicks=0, style={'margin-top': '10px'}),
        html.Button('Download Image', id='download-btn', n_clicks=0, style={'margin-top': '10px', 'display': 'none'}),
        html.Img(id='display-image', src='', style={'margin-top': '20px'}),
        dcc.Download(id='download-image')
    ])

    # Callback to update image display and show download button
    @app.callback(
        [Output('display-image', 'src'),
         Output('download-btn', 'style')],
        [Input('generate-btn', 'n_clicks')],
        [State('input-prompt', 'value'),
         State('input-guidance-scale', 'value'),
         State('input-steps', 'value')]
    )
    def update_image(n_clicks, prompt_text, guidance_scale, num_inference_steps):
        if n_clicks > 0 and prompt_text:
            image = generate_image(prompt_text, guidance_scale, num_inference_steps)
            if image:
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                return f'data:image/png;base64,{img_str}', {'display': 'inline-block'}
        return '', {'display': 'none'}

    # Callback to handle image download
    @app.callback(
        Output('download-image', 'data'),
        [Input('download-btn', 'n_clicks')],
        [State('display-image', 'src')]
    )
    def download_image(n_clicks, src):
        if n_clicks > 0 and src:
            img_str = src.split(',')[1]
            img_data = base64.b64decode(img_str)
            date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f'generated_image_{date_str}.png'
            return dcc.send_bytes(img_data, filename)

    return app
