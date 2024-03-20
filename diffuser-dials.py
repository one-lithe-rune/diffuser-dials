import gradio as gr
import PIL.Image as Image

from config.paths import BasePaths, APP_NAME
from config.args import args
from config.page import head_style
from gallery_ui import outputgallery, tab_select

def ui() -> gr.Blocks:
    with gr.Blocks(        
        css=BasePaths.stylesheet,
        head=head_style,
        analytics_enabled=False,
        title=APP_NAME,
        delete_cache=(7200, 7200),
    ) as diffuser_dials:
        logo = Image.open(BasePaths.images / "logo-medium.png")
        gr.Image(
            value=logo,
            show_label=False,
            interactive=False,
            elem_id="tab_bar_logo",
            show_download_button=False,
        )
        with gr.Tab("Gallery"):
            outputgallery.render()

    return diffuser_dials


if __name__ == "__main__":
    ui().launch(
        share=False,
        server_name=args.host,
        server_port=args.port,
        favicon_path=BasePaths.images / "logo-icon.png",
        allowed_paths=[BasePaths.output_dir],
        show_api=False,
        inbrowser=True,
    )
