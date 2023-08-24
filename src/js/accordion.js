export async function toggleAccordion(accordion, accordionContent) {
    const accordionContentDiv = document.getElementById(accordionContent);

    let accordionImage = accordion.querySelector("img").src;

    if (accordionImage.toLowerCase().includes("chevron_hyphen")) {
        console.log("Accordion doesn't have children");
        return;
    }

    const isOpen = accordion.classList.contains("open");

    if (isOpen) {
        /**
         * Close the modal:
         */
        accordion.setAttribute("aria-expanded", false);
        accordionContentDiv.setAttribute("aria-hidden", true);
        accordion.classList.remove("open");
        return;
    }


    accordion.setAttribute("aria-expanded", true);
    accordionContentDiv.setAttribute("aria-hidden", false);
    accordion.classList.add("open");
    return;

}