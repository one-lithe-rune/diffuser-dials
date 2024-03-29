import glob
import gradio as gr
import os
import subprocess
import sys

from PIL import Image

from config import args, paths
from metadata import displayable_metadata

import runners

# -- Functions for file, directory and image info querying

output_dir = paths.output_dir
available_runners = runners.all()

def outputgallery_filenames(subdir) -> list[str]:
    new_dir_path = os.path.join(output_dir, subdir)
    if os.path.exists(new_dir_path):
        filenames = [
            glob.glob(new_dir_path + "/" + ext)
            for ext in ("*.png", "*.jpg", "*.jpeg")
        ]

        return sorted(sum(filenames, []), key=os.path.getmtime, reverse=True)
    else:
        return []


def output_subdirs() -> list[str]:
    # Gets a list of subdirectories of output_dir and below, as relative paths.
    relative_paths = [
        os.path.relpath(entry[0], output_dir)
        for entry in os.walk(
            output_dir, followlinks=args.followlinks
        )
    ]

    # It is less confusing to always including the subdir that will take any
    # images generated today even if it doesn't exist yet
    if "." not in relative_paths:
        relative_paths.append(".")

    # sort subdirectories so that the date named ones we probably
    # created in this or previous sessions come first, sorted with the most
    # recent first. Other subdirs are listed after.
    generated_paths = sorted(
        [path for path in relative_paths if path.isnumeric()], reverse=True
    )
    result_paths = generated_paths + sorted(
        [
            path
            for path in relative_paths
            #if (not path.isnumeric()) and path != "."
        ]
    )

    return result_paths


# --- Define UI layout for Gradio

with gr.Blocks() as outputgallery:
    app_logo = Image.open(paths.images / "logo.png")

    with gr.Row(elem_id="outputgallery_gallery"):
        # needed to workaround gradio issue:
        # https://github.com/gradio-app/gradio/issues/2907
        dev_null = gr.Textbox("", visible=False)

        gallery_files = gr.State(value=[])
        subdirectory_paths = gr.State(value=output_subdirs())

        with gr.Column(scale=6):
            logo = gr.Image(
                label="No Images",
                value=app_logo,
                interactive=False,
                show_download_button=False,
                visible=True,
                show_label=True,
                elem_id="top_logo",
                elem_classes="logo_centered",
            )
            gallery = gr.Gallery(
                label="",
                value=gallery_files.value,
                visible=False,
                show_label=True,
                columns=4,
            )

        with gr.Column(scale=4):
            with gr.Group():
                with gr.Row(elem_id="output_subdir_container"):
                    with gr.Column(
                        scale=15,
                        min_width=160,
                    ):
                        subdirectories = gr.Dropdown(
                            label=f"Subdirectories of {output_dir}",
                            type="value",
                            choices=subdirectory_paths.value,
                            value="",
                            interactive=True,
                            # elem_classes="dropdown_no_container",
                            allow_custom_value=True,
                        )
                    with gr.Column(
                        scale=1,
                        min_width=32,
                        elem_classes="output_icon_button",
                    ):
                        open_subdir = gr.Button(
                            variant="secondary",
                            value="\N{open file folder}",
                            interactive=False,
                            size="sm",
                        )
                    with gr.Column(
                        scale=1,
                        min_width=32,
                        elem_classes="output_icon_button",
                    ):
                        refresh = gr.Button(
                            variant="secondary",
                            value="\u21BB",
                            size="sm",
                        )

            image_columns = gr.Slider(
                label="Columns shown", value=4, minimum=1, maximum=16, step=1
            )
            outputgallery_filename = gr.Textbox(
                label="Filename",
                value="None",
                interactive=False,
                show_copy_button=True,
            )
            with gr.Accordion(
                label="Parameter Information", open=True
            ) as parameters_accordian:
                image_parameters = gr.DataFrame(
                    headers=["Parameter", "Value"],
                    datatype=["str", "str"],
                    col_count=(2, "fixed"),
                    row_count=(1, "fixed"),
                    wrap=True,
                    elem_classes="output_parameters_dataframe",
                    value=[["Status", "No image selected"]],
                    interactive=True,
                    type="array",
                )
            with gr.Row():
                show_command=gr.Button(
                    value="Show command",
                )
                run_command=gr.Button(
                    value="Run command",
                )

            command_text=gr.TextArea(
                value="",
            )

    # --- Event handlers

    # TODO: use decorators to attach these handlers where we don't need to use '.then'

    def on_clear_gallery():
        return [
            gr.Gallery(
                value=[],
                visible=False,
            ),
            gr.Image(
                visible=True,
            ),
        ]

    def on_image_columns_change(columns):
        return gr.Gallery(columns=columns)


    def on_select_subdir(subdir, request: gr.Request) -> list:
        # evt.value is the subdirectory name
        new_images = outputgallery_filenames(subdir)
        new_label = (
            f"{len(new_images)} images in {os.path.join(output_dir, subdir)}"
        )
        local_client = request.headers["host"].startswith(
            "127.0.0.1:"
        ) or request.headers["host"].startswith("localhost:")
        return [
            new_images,
            gr.Gallery(
                value=new_images,
                label=new_label,
                visible=len(new_images) > 0,
            ),
            gr.Button(
                interactive=local_client,
            ),
            gr.Image(
                label=new_label,
                visible=len(new_images) == 0,
            ),
        ]


    def on_open_subdir(subdir):
        subdir_path = os.path.normpath(os.path.join(output_dir, subdir))

        if os.path.isdir(subdir_path):
            if sys.platform == "linux":
                subprocess.run(["xdg-open", subdir_path])
            elif sys.platform == "darwin":
                subprocess.run(["open", subdir_path])
            elif sys.platform == "win32":
                os.startfile(subdir_path)

    def on_refresh(current_subdir: str) -> list:
        # get an up-to-date subdirectory list
        refreshed_subdirs = output_subdirs()
        # get the images using either the current subdirectory or the most
        # recent valid one
        new_subdir = (
            current_subdir
            if current_subdir in refreshed_subdirs
            else refreshed_subdirs[0]
        )
        new_images = outputgallery_filenames(new_subdir)
        new_label = (
            f"{len(new_images)} images in "
            f"{os.path.join(output_dir, new_subdir)}"
        )

        return [
            gr.Dropdown(
                choices=refreshed_subdirs,
                value=new_subdir,
            ),
            refreshed_subdirs,
            new_images,
            gr.Gallery(
                value=new_images, label=new_label, visible=len(new_images) > 0
            ),
            gr.Image(
                label=new_label,
                visible=len(new_images) == 0,
            ),
        ]

    def on_new_image(subdir, subdir_paths) -> list:
        new_images = outputgallery_filenames(subdir)
        new_label = (
            f"{len(new_images)} images in "
            f"{os.path.join(output_dir, subdir)}"
        )

        return [
            new_images,
            gr.Gallery(
                value=new_images,
                label=new_label,
                visible=len(new_images) > 0,
            ),
            gr.Image(
                label=new_label,
                visible=len(new_images) == 0,
            ),
        ]

    def on_select_image(images: list[str], evt: gr.SelectData) -> list:
        # evt.index is an index into the full list of filenames for
        # the current subdirectory
        filename = images[evt.index]
        params = displayable_metadata(filename)

        if params:
            if params["source"] == "missing":
                return [
                    "Could not find this image file, refresh the gallery and update the images",
                    [["Status", "File missing"]],
                ]
            else:
                return [
                    filename,
                    gr.DataFrame(
                        value=list(map(list, params["parameters"].items())),
                        row_count=(len(params["parameters"]), "fixed"),
                    ),
                ]

        return [
            filename,
            gr.DataFrame(
                value=[["Status", "No parameters found"]],
                row_count=(1, "fixed"),
            ),
        ]

    def on_outputgallery_filename_change(filename: str) -> list:
        exists = filename != "None" and os.path.exists(filename)
        return [
            # disable or enable each of the sendto button based on whether
            # an image is selected
            gr.Button(interactive=exists),
            gr.Button(interactive=exists),
            gr.Button(interactive=exists),
            gr.Button(interactive=exists),
            gr.Button(interactive=exists),
            gr.Button(interactive=exists),
        ]

    # The time first our tab is selected we need to do an initial refresh
    # to populate the subdirectory select box and the images from the most
    # recent subdirectory.
    #
    # We do it at this point rather than setting this up in the controls'
    # definitions as when you refresh the browser you always get what was
    # *initially* set, which won't include any new subdirectories or images
    # that might have created since the application was started. Doing it
    # this way means a browser refresh/reload always gets the most
    # up-to-date data.
    def on_select_tab(subdir_paths, request: gr.Request):
        local_client = request.headers["host"].startswith(
            "127.0.0.1:"
        ) or request.headers["host"].startswith("localhost:")

        if len(subdir_paths) == 0:
            return on_refresh("") + [gr.update(interactive=local_client)]
        else:
            return (
                # Change nothing, (only untyped gr.update() does this)
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
            )

    def on_click_run_command(subdir, params):
        command = list(available_runners.values())[0].get_command(params, subdir)
        subprocess.run(command)
        return (
            command,
        )

    def on_click_show_command(subdir, params):
        return (
            list(available_runners.values())[0].get_command(params, subdir),
        )

    # clearing images when we need to completely change what's in the
    # gallery avoids current images being shown replacing piecemeal and
    # prevents weirdness and errors if the user selects an image during the
    # replacement phase.
    clear_gallery = dict(
        fn=on_clear_gallery,
        inputs=None,
        outputs=[gallery, logo],
        queue=False,
    )

    subdirectories.select(**clear_gallery).then(
        on_select_subdir,
        [subdirectories],
        [gallery_files, gallery, open_subdir, logo],
        queue=False,
    )

    open_subdir.click(on_open_subdir, inputs=[subdirectories], queue=False)

    refresh.click(**clear_gallery).then(
        on_refresh,
        [subdirectories],
        [subdirectories, subdirectory_paths, gallery_files, gallery, logo],
        queue=False,
    )

    image_columns.change(
        fn=on_image_columns_change,
        inputs=[image_columns],
        outputs=[gallery],
        queue=False,
    )

    gallery.select(
        on_select_image,
        [gallery_files],
        [outputgallery_filename, image_parameters],
        queue=False,
    )

    run_command.click(
        fn=on_click_show_command,
        inputs=[subdirectories,image_parameters],
        outputs=[command_text],
    ).then(
        fn=on_click_run_command,
        inputs=[subdirectories,image_parameters],
        outputs=[command_text]
    ).then(
        fn=on_new_image,
        inputs=[subdirectories, subdirectory_paths],
        outputs=[gallery_files, gallery, logo],
        show_progress="none",
    )

    # @image_parameters.input(inputs=image_parameters)
    # def on_parameters_input(value: list):
    #     print(value)

    # We should have been given the .select function for our tab, so set it up
    # def tab_select(select):
    #     select(
    #         fn=on_select_tab,
    #         inputs=[subdirectory_paths],
    #         outputs=[
    #             subdirectories,
    #             subdirectory_paths,
    #             gallery_files,
    #             gallery,
    #             logo,
    #             open_subdir,
    #         ],
    #         queue=False,
    #     )

