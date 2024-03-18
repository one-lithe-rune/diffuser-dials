// workaround gradio after 4.7, not applying any @media rules form the custom .css file

// TODO: This breaks Gradio 4.21

() => {
    // 1536px rules

    const mediaQuery1536 = window.matchMedia('(min-width: 1536px)')

    function handleWidth1536(event) {

        // display in full width for desktop devices
        document.querySelectorAll(".gradio-container")
            .forEach( (node) => {
                if (event.matches) {
                    node.classList.add("gradio-container-size-full");
                } else {
                    node.classList.remove("gradio-container-size-full")
                }
            });
    }

    mediaQuery1536.addEventListener("change", handleWidth1536);
    mediaQuery1536.dispatchEvent(new MediaQueryListEvent("change", {matches: window.innerWidth >= 1536}));
}
