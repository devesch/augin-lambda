/**
 * Máscaras úteis para diversos projetos.
 * Modo de usar: oninput="formatToCPF(this)"
 */

export async function copyValueToClipboard(input) {
  navigator.clipboard.writeText(input.value);

  let translate_response = await apiCaller('translate', {
    'key': "Copiado"
  });
  input.innerHTML = translate_response["success"] + "!";
  await sleep(2000);
}

function formatToCNPJ(string) {
  // Remove tudo o que não é dígito
  string.value = string.value.replace(/\D/g, "");
  // Coloca ponto entre o segundo e o terceiro dígitos
  string.value = string.value.replace(/^(\d{2})(\d)/, "$1.$2");
  // Coloca ponto entre o quinto e o sexto dígitos
  string.value = string.value.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
  // Coloca uma barra entre o oitavo e o nono dígitos
  string.value = string.value.replace(/\.(\d{3})(\d)/, ".$1/$2");
  // Coloca um hífen depois do bloco de quatro dígitos
  string.value = string.value.replace(/(\d{4})(\d)/, "$1-$2");
  return string.value;
}

function formatToCPF(string) {
  // Remove tudo o que não é dígito
  string.value = string.value.replace(/\D/g, "");
  // Coloca um ponto entre o terceiro e o quarto dígitos
  string.value = string.value.replace(/(\d{3})(\d)/, "$1.$2");
  // de novo (para o segundo bloco de números)
  string.value = string.value.replace(/(\d{3})(\d)/, "$1.$2");
  // Coloca um hífen entre o terceiro e o quarto dígitos
  string.value = string.value.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
  return string.value;
}

function formatToCEP(string) {
  // Remove tudo o que não é dígito
  string.value = string.value.replace(/\D/g, "");
  // Coloca um ponto entre o segundo e terceiro dígitos e um hífen entre o quinto e sexto.
  string.value = string.value.replace(/(\d{2})(\d{3})(\d)/, "$1.$2-$3");
  return string.value;
}

function formatToCellphone(string) {
  // Remove tudo o que não é dígito
  string.value = string.value.replace(/\D/g, "");
  // Coloca parênteses em volta dos dois primeiros dígitos e espaço após eles.
  // Pega os 5 primeiros dígitos após o DDD e coloca um hífen entre eles e os quatro últimos dígitos.
  string.value = string.value.replace(/(\d{2})(\d{5})(\d)/, "($1) $2-$3");
  return string.value;
}

function hideSearchListResults(search) {
  if (search.nextElementSibling) {
    if (detectClickOutsideElement(search)) {
      search.nextElementSibling.addClass("none");
      return false;
    }

    search.nextElementSibling.removeClass("none");
    return true;
  } else {
    console.error("toggleInputSearches error: element does not have next sibling!");
  }
};

function detectClickOutsideElement(htmlElement, elementMethod) {
  htmlElement.addEventListener("blur", function () {
    console.log("Focus Out no Elemento");
    elementMethod(htmlElement);
  }, true);

  htmlElement.addEventListener("keydown", function (event) {
    if (event.key === "Escape" || event.key === 27) {
      console.log("Esc no Elemento");
      elementMethod(htmlElement);
    }
  }, true);
}

const searches = document.querySelectorAll(".search");
if (searches) {
  searches.forEach(function (search) {
    detectClickOutsideElement(search, hideSearchListResults(search));
  });
}


export async function lazyloadYoutubeIframes() {
  if ('IntersectionObserver' in window) {
      let youtube = document.querySelectorAll(".youtube-player");

      for (let i = 0; i < youtube.length; i++) {

          let source = "https://img.youtube.com/vi/"+ youtube[i].dataset.id +"/sddefault.jpg";

          let image = new Image();
          image.setAttribute("src", source);
          image.setAttribute("width", youtube[i].dataset.width);
          image.setAttribute("height", youtube[i].dataset.height);
          image.setAttribute("alt", youtube[i].dataset.title);
          image.setAttribute("loading", "lazy");
          image.classList.add("main-video");
          image.addEventListener("load", function() {
              youtube[ i ].appendChild( image );
          }(i));

          youtube[i].addEventListener("click", function() {

              let iframe = document.createElement("iframe");

              iframe.setAttribute("frameborder", "0");
              iframe.setAttribute("allowfullscreen", "");
              iframe.setAttribute("width", this.dataset.width);
              iframe.setAttribute("height", this.dataset.height);
              iframe.setAttribute("src", "https://www.youtube.com/embed/"+ this.dataset.id);
              iframe.setAttribute("title", this.dataset.title);
              iframe.setAttribute("allow", "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share");
              iframe.setAttribute("loading", "lazy");
              iframe.classList.add("main-video");

              this.replaceChild(iframe, image);

          } ); 
      };

      let observer = new IntersectionObserver((entries, observer) => {
          entries.forEach(entry => {
              if(entry.isIntersecting){
                  let lazyIframe = entry.target;
                  lazyIframe.click();
                  observer.unobserve(lazyIframe);
              }
          })
      }, {threshold: 0.1});

      youtube.forEach(lazyIframe => {
          observer.observe(lazyIframe);
      });
  } else {
      console.error("Intersect Observer is not compatible with your browser, insert a fallback here.");
  }
}


const AnchorLinkUtils = {
  getPositionOfElementByHref: async function (element) {
    const href = element.getAttribute('href').split("/").pop();
    return document.querySelector(href).offsetTop;
  },

  scrollToPositionWithSmoothBehavior: async function (position) {
    window.scroll({
      top: position,
      behavior: 'smooth'
    });
  },

  handleInternalLinkClick: async function (event) {
    event.preventDefault();
    const fixedHeaderHeight = document.querySelector('header').offsetHeight;
    const targetElementPosition = (await AnchorLinkUtils.getPositionOfElementByHref(event.target) - fixedHeaderHeight);
    AnchorLinkUtils.scrollToPositionWithSmoothBehavior(targetElementPosition);
  },

  attachClickListenersToInternalLinks: function () {
    const internalLinks = document.querySelectorAll('a[href*="#"]');
    if (internalLinks.length > 0) {
      internalLinks.forEach(link => {
        link.addEventListener('click', AnchorLinkUtils.handleInternalLinkClick);
      });
    }
  }
};

export default AnchorLinkUtils;