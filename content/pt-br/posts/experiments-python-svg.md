authors: Kennedy Richard S. Guerra
author-urls: https://kennedyrichard.com
keywords: SVG
          gráficos vetoriais escaláveis
          gráficos vetoriais
          cairoSVG
description: Experimentos com Python e SVG no Nodezator
publish-date: 2023-10-23
include-comment-section: True


# Manipulando imagens SVG com Python (pequena demonstração)

<img class="img-fluid mb-4" src="https://i.imgur.com/Q5oYm5Z.png" alt="Captura de tela do Nodezator mostrando um grafo com SVG renderizado no fim como uma superfície/imagem estática." />



## Introdução

Tenho feito diferentes experimentos com Nodezator e outras bibliotecas Python a fim de identificar tarefas de programação que têm sinergia com uma abordagem de edição de nós. Este experimento mostra o que tenho aprendido sobre Python e imagens [SVG](https://pt.wikipedia.org/wiki/SVG). O que aprendi e mostro aqui é na verdade muito útil independente de você utilizar código Python diretamente ou por meio de edição de nós.

Como sempre, estarei usando o app Nodezator, um editor de nós Python generalista e gratuito. Este não é um guia abrangente, apenas simples demonstrações usando tecnologias que são familiares para mim. A biblioteca pygame utilizada refere-se a [pygame-ce](https://pyga.me) (em inglês), o fork que representa uma nova edição da lançada por uma comunidade, que é a biblioteca correntemente utlizada pelo Nodezator.

Os blocos de código que aparecem aqui e ali neste post são apenas representações brutas do código mostrado no grafo. Exceto numa demonstração específica que utiliza nós customizados que criei, todas as demonstrações restantes usam nós padrão que já vem prontos para uso no Nodezator. Eles são nós muito simples, no entanto, criados somente para a demosntração, motivo pelo qual eu não publiquei o código-fonte aqui. Se quiser o código-fonte basta pedir e te enviarei imediatamente.

Este post também está disponível em vídeo (em inglês):

<div class="ratio ratio-16x9 my-4">
    <iframe src="https://www.youtube.com/embed/kMGc5rxuQfg"></iframe>
</div>



## Usando pygame para carregar imagens SVG

<img class="img-fluid mb-4" alt="Captura de tela do Nodezator mostrando imagem SVG carregada como uma superfície." src="https://i.imgur.com/90HPeKd.png" />

Pygame/pygame-ce 2 pode carregar imagens SVG como objetos Surface (superfície), isto é, como imagens estáticas.

Ao passar o caminho para o arquivo para a função load() de pygame.image, o arquivo é carregado como uma Surface imediatamente. O grafo mostrado na imagem é aproximadamente equivalente à chamada abaixo (mas a superfície resultante é passada para o nó `view_surface` no Nodezator):

```python
surface = pygame.image.load('path_to_svg_image.svg')
```

Este método não oferece nenhum controle sobre a saída. Não podemos controlar o tamanho da imagem como poderíamos dentro de uma página web. Adicionalmente, não entrarei em detalhes aqui, mas o suporte a SVG oferecido por pygame é limitado. Independente disso, no entanto, eu diria que o subconjunto do SVG que pygame/pygame-ce suporta é mais do que suficiente para a maioria dos propósitos, incluindo coisas avançadas.


## Usando pygame para carregar dados SVG de uma string

<img class="img-fluid mb-4" alt="Captura de tela do Nodezator mostrando texto SVG convertido numa superfície." src="https://i.imgur.com/WJ1WrbN.png" />

Vamos agora ver outra possibilidade. As pessoas às vezes esquecem que SVG é apenas um arquivo de texto com instruções para criar formas. Isso significa que podemos facilmente criar dados SVG por meio da escrita de nossas próprias instruções.

Neste exemplo escrevi um texto simples descrevendo a bandeira do Japão em SVG. O texto SVG:

```svg
<svg width="300" height="200">
    <rect x="0" y="0" width="300" height="200" fill="white" />
    <circle cx="150" cy="100" r="60" fill="red" />
</svg>
```

Então converto ele em bytes, passo esses bytes para um objeto BytesIO, que funciona do mesmo jeito que um arquivo e passo esse objeto BytesIO para a função load() do módulo de imagem de pygame:

```python
from io import BytesIO

import pygame


svg_text = """
<svg width="300" height="200">
    <rect x="0" y="0" width="300" height="200" fill="white" />
    <circle cx="150" cy="100" r="60" fill="red" />
</svg>
""".strip()

svg_bytes = bytes(svg_text, encoding='utf-8')

bytestream = BytesIO(svg_bytes)

surface = pygame.image.load(bytestream)
```


## Usando uma abordagem orientada a objetos para descrever formas SVG (e controlar tamanho)

<img class="img-fluid mb-4" alt="Captura de tela do Nodezator mostrando objects SVG XML convertidos numa superfície." src="https://i.imgur.com/TDxxZf2.png" />

Além de ser um arquivo de texto, SVG é na verdade um arquivo de linguagem de marcação. É apenas XML. E, como Python tem uma biblioteca padrão para lidar com objetos XML com uma abordagem orientada a objetos, você pode manipular formas SVG com ela. Chama-se [xml.etree.ElementTree](https://docs.python.org/pt-br/3/library/xml.etree.elementtree.html).

Aqui criei funções customizadas para encapsular parte do comportamento da biblioteca como nós.

Então, tenho algums objetos básicos novamente. Os coloco dentro de um objeto SVG, converto-os numa bytestring XML e faço o mesmo que fiz anteriormente: crio um objeto que funciona como um arquivo e o passo para pygame.image.load():

```python
### standard library imports

from xml.etree.ElementTree import tostring

from io import BytesIO


### third-party import
import pygame


### local imports (functions representing nodes; they use ElementTree internally)

from svg_elements.elements.get_svg.__main__ import get_svg
from svg_elements.elements.get_svg_circle.__main__ import get_svg_circle
from svg_elements.elements.get_svg_rect.__main__ import get_svg_rect


svg_rect = get_svg_rect(0, 0, 300, 200, 0, 0, (255, 255, 255), 1.0, (0, 0, 0), 0, 1.0)
svg_circle = get_svg_circle(150, 100, 60, (255, 0, 0), 1.0, (0, 0, 0), 0, 1.0)

children = (svg_rect, svg_circle)

svg_obj = get_svg(300, 200, children)

svg_bytes = tostring(svg_obj, 'utf-8', 'xml', short_empty_elements=True)

bytestream = BytesIO(svg_bytes)

surface = pygame.image.load(bytestream)
```

Novamente, este código resulta na bandeira do Japão.

Antes de prosseguirmos para a próxima demonstração, gostaria de demonstrar outra possibilidade relacionada a esta demonstração.

Como temos acesso aos atributos individuais e seus valores, podemos usá-los para controlar a escala da superfície gerada como desejarmos.

Por exemplo, ao invés de digitar valores em cada nó (em cada chamada de função), posso apenas especificar um dos valores e ter os demais valores calculados com base nele. Cheque os nós extras na imagem abaixo:

<img class="img-fluid mb-4" alt="Captura de tela do Nodezator mostrando o comprimento (width) sendo passado por muitos nós de operações." src="https://i.imgur.com/EoMVqUw.png" />

Poderia tê-los organizado melhor, mas como disse, esta é apenas uma demonstração rápida. Posso apenas conectar os valores calculados aos nós correspondentes. Uam vez que faço isso, posso especificar somente o comprimento (width) e o resto dos valores é calculado automaticamente com base nele. Aqui está como isso tudo se traduz em código Python (é quase o mesmo código do bloco anterior, mas definimos o comprimento primeiro e fazemos alguns cálculos para definir os outros valores utilizados para criar objetos SVG):

```python
### standard library imports

from xml.etree.ElementTree import tostring

from io import BytesIO


### third-party import
import pygame


### local imports (functions representing nodes; they use ElementTree internally)

from svg_elements.elements.get_svg.__main__ import get_svg
from svg_elements.elements.get_svg_circle.__main__ import get_svg_circle
from svg_elements.elements.get_svg_rect.__main__ import get_svg_rect



### we define the width...
width = 300

### and the rest of the values are calculated based on it

height = width / 3 * 2
center_x = width / 2
center_y = height / 2
radius = height / 5 * 3 / 2

### the rest of the code remains the same

svg_rect = get_svg_rect(0, 0, width, height, 0, 0, (255, 255, 255), 1.0, (0, 0, 0), 0, 1.0)
svg_circle = get_svg_circle(center_x, center_y, radius, (255, 0, 0), 1.0, (0, 0, 0), 0, 1.0)

children = (svg_rect, svg_circle)

svg_obj = get_svg(width, height, children)

svg_bytes = tostring(svg_obj, 'utf-8', 'xml', short_empty_elements=True)

bytestream = BytesIO(svg_bytes)

surface = pygame.image.load(bytestream)
```

Ao aumentar o comprimento podemos ver que na imagem abaixo que a superfície final é maior do que a original, mas retêm suas proporções:

<img class="img-fluid mb-4" alt="Captura de tela do Nodezator mostrando uma imagem renderizada maior resultante da mudança no comprimento (width)." src="https://i.imgur.com/YsGmEgW.png" />


Como pode ver, conseguimos controlar o comprimento com precisão e o resto da imagem foi renderizada com as mesmas proporções.


## Usando pygame para carregar dados SVG de uma string (e controlar tamanho)


Outra possibilidade útil é a de controlar o tamanho da imagem renderizada usando transformações SVG (transforms). Ainda que limitado, o suporte a SVG de pygame ainda nos permite alcançar muitas coisas. Uma delas é a possibilidade de facilmente redimensionar formas SVG que queremos renderizar e assim controlar o resultado final.

Aqui temos um grafo similar ao anterior, o que usamos para ilustrar como carregar SVG a partir de texto, onde definimos a bandeira do Japão:

<img class="img-fluid mb-4" alt="Captura de tela do Nodezator mostrando texto SVG convertido numa superfície." src="https://i.imgur.com/bJc0spT.png" />

Então, aqui está o texto SVG novamente...

```svg
<svg width="300" height="200">
    <rect x="0" y="0" width="300" height="200" fill="white" />
    <circle cx="150" cy="100" r="60" fill="red" />
</svg>
```

Agora, aqui está a mágica: se omitirmos o comprimento e altura no elemento SVG, o tamanho da imagem resultante será o mesmo da área ocupada pelas formas. Ainda por cima podemos aplicar transformações (transforms) bem lisas nas formas ao agruparmos elas juntas e definirmos as transformações que queremos aplicar. Aqui está o texto SVG resultante:

```svg
<svg>
    <g transform="scale(2)">
    <rect x="0" y="0" width="300" height="200" fill="white" />
    <circle cx="150" cy="100" r="60" fill="red" />
    </g>
</svg>
```

Agora vejamos a superfície resultante:

<img class="img-fluid mb-4" alt="Captura de tela do Nodezator mostrando texto SVG convertido numa superfície." src="https://i.imgur.com/q7W1Wt3.png" />

Como podemos ver, uma transformação de redimensionamento bem lisa foi aplicada. Novamente, isto permite bastante controle sobre a imagem resultante. Vamos também girar a forma agora.

```svg
<svg>
    <g transform="scale(2) rotate(15)">
    <rect x="0" y="0" width="300" height="200" fill="white" />
    <circle cx="150" cy="100" r="60" fill="red" />
    </g>
</svg>
```

Vejamos o resultado...

<img class="img-fluid mb-4" alt="Captura de tela do Nodezator mostrando texto SVG convertido numa superfície." src="https://i.imgur.com/jxpZ6f3.png" />

Novamente, rotação e dimensionamentos bem lisos.

Vamos também distorcer/inclinar a image no eixo x!

```svg
<svg>
    <g transform="scale(2) rotate(15) skewX(25)">
    <rect x="0" y="0" width="300" height="200" fill="white" />
    <circle cx="150" cy="100" r="60" fill="red" />
    </g>
</svg>
```

De novo, temos resultados interessantes:

<img class="img-fluid mb-4" alt="Captura de tela do Nodezator mostrando texto SVG convertido numa superfície." src="https://i.imgur.com/xy9BNxr.png" />

Vamos prossegir à próxima demonstração...


## Manipulando SVG com cairoSVG

Como disse antes, pygame tem suporte limitado ao SVG. Como demonstrado, no entanto, isso ainda significa que bastante coisa pode ser feito com pygame.

No entanto, há alternativas. Não fiz uma pesquisa abrangente do tópico, mas achei uma biblioteca muito simples e poderosa que é muito útil. Chama-se [cairoSVG](https://cairosvg.org/). Ela pode ser usada para converter SVG para muitos formatos e tem melhor suporte a SVG do que pygame.

Estaremos utilizando uma função chamada `svg2png()` daquela biblioteca. No grafo abaixo eu a utilizo para converter SVG para PNG, e então carrego os dados PNG como uma Surface de pygame, para que possamos visualizar.

<img class="img-fluid mb-4" alt="Captura de tela do Nodezator mostrando arquivo SVG convertido em PNG com cairoSVG, visualizado como uma Surface em pygame." src="https://i.imgur.com/rRUYFKP.png" />

O grafo seria aproximadamente equivalente a:

```python
from io import BytesIO

from cairosvg import svg2png

import pygame


png_data = svg2png(url="path_to_svg_file.svg")

bytestream = BytesIO(png_data)

surface = pygame.image.load(bytestream)
```

Ainda que não mostrado na imagem, CairoSVG oferece opções adicionais ao converter SVG. Permite-nos direto controle do formato gerado por meio de parâmetros. Podemos usar as opções nas funções utilizadas para converter arquivos SVG. Por exemplo, a função `svg2png()` tem parâmetros como `scale` (escala/tamanho), `output_width` (comprimento da saída) e `output_height` (largura/altura da saída) que permite a usuários especificar com precisão o tamanho, comprimento ou largura/altura da imagem PNG gerada.

Por exemplo, uma leve mudança no código Python anterior nos permitiria controlar diretamente o comprimento do nosso arquivo, desse jeito:

```python
from io import BytesIO

from cairosvg import svg2png

import pygame


# simplesmente adicionei output_width à chamada e agora podemos especificar
# qualquer comprimento que quisermos
png_data = svg2png(url="path_to_svg_file.svg", output_width=400)

bytestream = BytesIO(png_data)

surface = pygame.image.load(bytestream)
```

Há outras opções úteis, mas não as cobriremos aqui.


## Manipulando SVG com cairoSVG (texto SVG)

Assim como pygame, também podemos usar texto SVG. Nós passamos o texto SVG como uma bytestring para a função svg2png(), já que ela tem uma opção para isso.

Aqui está o texto SVG:

```svg
<svg width="300" height="200">
    <rect x="0" y="0" width="300" height="200" fill="white" />
    <circle cx="150" cy="100" r="60" fill="red" />
</svg>
```

Tornamos esse texto em bytes e passamos para svg2png() usando a opção "bytestring".

O grafo resultante é assim:

<img class="img-fluid mb-4" alt="Captura de tela do Nodezator mostrando texto SVG convertido em PNG com cairoSVG, visualizado como uma Surface de pygame." src="https://i.imgur.com/ElbN3QI.png" />

E aqui está o código Python equivalente:

```python
from io import BytesIO

from cairosvg import svg2png

import pygame


svg_text = """
<svg width="300" height="200">
    <rect x="0" y="0" width="300" height="200" fill="white" />
    <circle cx="150" cy="100" r="60" fill="red" />
</svg>
""".strip()

svg_bytes = bytes(svg_text, encoding='utf-8')

png_data = svg2png(bytestring=svg_bytes)

bytestream = BytesIO(png_data)

surface = pygame.image.load(bytestream)
```


## Comparando suporte SVG de cairoSVG e pygame

Adicionalmente, como disse antes, cairoSVG tem melhor suporte para SVG, de maneira que pode renderizar coisas que pygame não seria capaz de renderizar. Por exemplo, a imagem abaixo mostra o mesmo arquivo SVG assim como renderizado por pygame (esquerda) e cairoSVG (direita):

<img class="img-fluid mb-4" alt="Duas imagens lado a lad, representando o mesmo arquivo SVG renderizado com pygame-ce (esquerda) e cairoSVG (direita)." src="https://i.imgur.com/HXorWyF.png" />

As imagens foram renderizadas sem gerar erros, mas cairoSVG foi capaz de renderizar mais elementos do que pygame. O arquivo SVG pode ser achado [aqui](https://en.wikipedia.org/wiki/File:Boolean_operations_on_shapes-en.svg).

Novamente, gostaria de reforçar que isto não torna pygame inapropriado para trabalhar com SVG. O suporte a SVG de pygame ainda é muito útil e pode ser usado para muitas coisas. No entanto, é ótimo que tenhamos alternativas como cairoSVG, que pode fazer ainda mais, de maneira que possamos usá-la quando for necessário.


## Funcionalidades SVG de pygame-ce

Gostaria de terminar esta demonstração mostrando algumas coisas úteis que pode ser facilmente feitas com SVG usando pygmae. Coisas que doutra maneira iriam requerer trabalho demais usando outros métodos.

A imagem abaixo mostra imagens SVG renderizadas com pygame-ce:

<img class="img-fluid mb-4" alt="Várias imagens lado a lado, representando imagens SVG renderizadas com pygame-ce." src="https://i.imgur.com/jwFiMHM.png" />

Então, por examplo, você pode criar coisas como as linhas tracejadas indicadas pela letra A na imagem acima. Ou um caminho de curva lisa mostrado com a letra B. Ou, por que não, um caminhho tracejado como mostrado na letra C. E mesmo gradientes, como mostrado na letra D.

Aqui estão os respectivos textos SVG:

A:

```svg
<svg width="300" height="200">
    <rect x="0" y="0" width="300" height="200" fill="rgb(230, 230, 230)" />
    <line x1="10" y1="190" x2="290" y2="10" stroke="black" stroke-width="7" stroke-dasharray="10" />
</svg>
```

B:

```svg
<svg width="300" height="200">
    <rect x="0" y="0" width="300" height="200" fill="rgb(230, 230, 230)" />
    <path d="M10 10 q0 90 140 90 q140 0 140 90" fill="none" stroke="black" stroke-width="8" />
</svg>
```

C:

```svg
<svg width="300" height="200">

    <rect x="0" y="0" width="300" height="200" fill="rgb(230, 230, 230)" />

    <path
        d="M10 10 q0 90 140 90 q140 0 140 90" fill="none" stroke="black" stroke-width="8"
        stroke-dasharray="10"
    />

</svg>
```

D:

```svg
<svg width="200" height="200">

<defs>
  <radialGradient id="sampleGradient">
     <stop offset="0%" stop-color="rgb(255, 120, 120)" />
     <stop offset="100%" stop-color="rgb(185, 0, 0)" />
  </radialGradient>
</defs>

<rect x="0" y="0" width="200" height="200" fill="url(#sampleGradient)" />

</svg>
```


## Conclusão

E com isso, concluimos esta breve demonstração.

Por favor, considere dar suporte ao desenvolvimento e manutenção do Nodezator [se tornando um patrão](https://patreon.com/KennedyRichard) (site em inglês, mas permite mudar interface para português do Brasil) do projeto Indie Smiths ou usando outra das muitas [opções de doação disponíveis](https://indiesmiths.com/pt-br/doe). Também se inscreva no nosso canal no YouTube, [@IndieSmiths](https://youtube.com/@IndieSmiths) (em inglês), e nos siga nas nossas redes sociais, [Twitter/X](https://x.com/KennedyRichard), [mastodon/fosstodon](https://fosstodon.org/@KennedyRichard), [bluesky](https://bsky.app/profile/kennedyrichard.com) e mais.
