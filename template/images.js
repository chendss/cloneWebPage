window.addEventListener('load', () => {
  const images = [...document.querySelectorAll('img')]
  images.forEach((img) => {
    img.addEventListener('click', () => {
      const src = img.src
      window.open(src)
    })
  })
})