authors: Kennedy Richard S. Guerra
author-urls: https://kennedyrichard.com
keywords: asciimath
          notação matemática
          py_asciimath
          sympy
description: Renderizando notação matemática com as bibliotecas ASCIIMath, py_asciimath and sympy no Nodezator
publish-date: 2023-09-23
include-comment-section: True

# Renderize notação matemática com ASCIIMath usando as bibliotecas py_asciimath e sympy

<img class="img-fluid mb-4" src="https://i.imgur.com/CDgj8yf.png" alt="Captura de tela do Nodezator demonstrando a conversão de código ASCIIMath numa superfície renderizada." />

Um usuário me pediu por suporte a ASCIIMath no Nodezator, isto é, que fosse possível tornar ASCIIMath (uma linguagem de marcação para representar notação matemática) no imagem renderizada correspondente. Felizmente, isso já podia ser feito no Nodezator! Nodezator é apenas um ambiente baseado em nós para objetos chamáveis de Python, de maneira que pode utilizar praticamente qualquer código/biblioteca Python disponíveis. Tudo que tive de fazer foi fazer alguns experimentos com bibliotecas Python disponíveis e a solução a que cheguei foi a solução demonstrada no vídeo abaixo:

<div class="ratio ratio-16x9 my-4">
    <iframe src="https://www.youtube.com/embed/F8BVAqgxBwQ"></iframe>
</div>

Nela, uso a biblioteca [py_asciimath](https://github.com/belerico/py_asciimath) para converter o código ASCIIMath num formato que é mais abrangentemente suportado, que é o Latex. O código Latex gerado pode ser facilmente renderizado numa imagem pela biblioteca [sympy](https://www.sympy.org/en/index.html), usando sua função `preview`. Para `sympy.preview` funcionar para este propósito, no entanto, você deve garantir que o comando `latex` está disponível no seu sistema, já que ele é utilizado internamente pelo sympy para fazer a renderização. Latex está disponível para todos os principais sistemas. É possível instalar apenas algumas partes dele dependendo de seus propósitos específicos, mas como não tinha certeza que partes dele eram necessárias para renderização de notação matemática, decidi fazer uma instalação completa, que é o que recomendo. Tenha em mente que é um download relativamente grande (alguns gigabytes).

Essas operações resultaram na criação de 02 nós customizados, `asciimath2latex` e `latex2surface`:

<img class="mb-4" src="https://i.imgur.com/y8b3yyG.png" alt="Nós para converter código ASCIIMath numa superfície renderizada (imagem)." />

Aqui estão os códigos-fonte desses nós:

Nó `asciimath2latex`:

```python
### third-party import
from py_asciimath.translator.translator import ASCIIMath2Tex



## translator callable
latex_from_asciimath = ASCIIMath2Tex(log=False, inplace=True).translate


## main callable

def asciimath2latex(asciimath_code:str='') -> [
    {'name': 'latex_code', 'type': str}
]:
    return latex_from_asciimath(
        asciimath_code,
        displaystyle=True,
        from_file=False,
        pprint=False,
    )


main_callable = asciimath2latex
```

Nó `latex2surface`:

```python
### standard library import
from io import BytesIO


### third-party imports

## pygame-ce

from pygame import Surface

from pygame.image import load as load_image


## sympy
from sympy import preview



def latex2surface(
    latex_code: str = '',
    font_size_prefix : {
        'widget_name': 'option_menu',
        'widget_kwargs': {
            'options': [
                'none',
                r'\tiny',
                r'\scriptsize',
                r'\footnotesize',
                r'\small',
                r'\normalsize',
                r'\large',
                r'\Large',
                r'\LARGE',
                r'\huge',
                r'\Huge',
            ],
        },
        'type': str,
    } = r'\Large',
) -> [
    {'name': 'surface', 'type': Surface}
]:

    ### add font size prefix if requested

    if font_size_prefix != 'none':
        latex_code = font_size_prefix + latex_code

    ### create bytes stream and populate it with bytes
    ### representing rendered PNG file

    bytes_io = BytesIO()

    preview(
        latex_code,
        output='png',
        viewer='BytesIO',
        outputbuffer=bytes_io,
    )

    ### change the stream position to start of stream
    ### (this way the bytes can be read properly)
    bytes_io.seek(0)

    ### convert bytes stream (a file-like object), into
    ### a surface
    surface = load_image(bytes_io, 'file.png')

    ### close the bytes stream, since we won't need it anymore
    bytes_io.close()

    ### finally return the surface
    return surface


main_callable = latex2surface
```

Você pode usar estes códigos-fonte como quiser. Na sua maior parte são apenas execuções de funções de bibliotecas externas de qualquer modo (mas mesmo se eu fosse licenciar esse código, usaria uma licença de domínio público, como fiz com o Nodezator e outros subprojetos do projeto Indie Smiths). Se você não sabe como carregar nós no Nodezator or como usar o app como um todo, há um manual online com toda informação necessária (em inglês): [https://manual.nodezator.com](https://manual.nodezator.com).

Os outros nós na demonstração do vídeo são nós prontos para uso que já vêm com o Nodezator. Para visualizar a superfície, usei o nó `view_surface` (menu de popup > nós gerais de visualização > `view_surface`), mas antes eu usei o nó `increase_surf_border` (aumentar borda da superfície) (menu de popup > pygame-ce > Encapsulações > `increase_surf_border`), com a cor configurada para branco para adicionar uma border ao redor (para servir como espaçamento interno). Isto não é mostrado no vídeo, mas se o usuário quiser, a superfície pode também ser salva no disco rígido como um arquivo de imagem (.png/.jpg) com o nó `save_surf_to_file` node (menu de popup > pygame-ce > pygame.image > `save_surf_to_file`).

Aqui está o link para a discussão original entre mim e o usuário (em inglês): [https://github.com/IndieSmiths/nodezator/discussions/67](https://github.com/IndieSmiths/nodezator/discussions/67).
