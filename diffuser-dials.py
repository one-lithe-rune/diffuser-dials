import gradio as gr
import PIL.Image as Image

from config import paths, args, head_style, APP_NAME
from gallery_ui import outputgallery


def ui() -> gr.Blocks:
    with gr.Blocks(
        css=paths.stylesheet,
        head=head_style,
        analytics_enabled=False,
        title=APP_NAME,
        delete_cache=(7200, 7200),
    ) as diffuser_dials:
        logo = Image.open(paths.images / "logo-medium.png")
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
    # allow direct serving of images from the outputdir if self-hosting
    # TODO: Make this a separate non-default command line option
    if args.host in ["localhost", "127.0.0.1", "::1"]:
        gr.set_static_paths([paths.output_dir])

    ui().launch(
        share=False,
        server_name=args.host,
        server_port=args.port,
        favicon_path=paths.images / "logo-icon.png",
        allowed_paths=[paths.output_dir],
        show_api=False,
        inbrowser=True,
    )
else:
    demo = ui()
