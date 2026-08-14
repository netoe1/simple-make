from pathlib import Path
import re
import sys


MAKEFILE_PADRAO = Path("Makefile")
BAT_SAIDA_PADRAO = Path("simple-make.bat")


class MakefileParser:
    def __init__(self, caminho_makefile: Path):
        self.caminho_makefile = caminho_makefile
        self.variaveis = {}
        self.targets = {}

    def parse(self):
        target_atual = None

        linhas = self.caminho_makefile.read_text(encoding="utf-8").splitlines()

        for numero_linha, linha_original in enumerate(linhas, start=1):
            linha = linha_original.rstrip()

            if self._linha_vazia_ou_comentario(linha):
                continue

            if self._eh_variavel(linha):
                nome, valor = self._parse_variavel(linha)
                self.variaveis[nome] = valor
                target_atual = None
                continue

            if self._eh_target(linha):
                nome_target, dependencias = self._parse_target(linha)

                self.targets[nome_target] = {
                    "dependencias": dependencias,
                    "comandos": []
                }

                target_atual = nome_target
                continue

            if self._eh_comando(linha_original):
                if target_atual is None:
                    raise SyntaxError(
                        f"Linha {numero_linha}: comando encontrado sem target."
                    )

                comando = linha_original.strip()
                self.targets[target_atual]["comandos"].append(comando)
                continue

            raise SyntaxError(
                f"Linha {numero_linha}: sintaxe nao suportada: {linha_original}"
            )

        return self.variaveis, self.targets

    def _linha_vazia_ou_comentario(self, linha: str) -> bool:
        return not linha.strip() or linha.lstrip().startswith("#")

    def _eh_variavel(self, linha: str) -> bool:
        return re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*=\s*.*$", linha) is not None

    def _parse_variavel(self, linha: str):
        partes = linha.split("=", 1)
        nome = partes[0].strip()
        valor = partes[1].strip()
        return nome, valor

    def _eh_target(self, linha: str) -> bool:
        return re.match(r"^[A-Za-z0-9_.-]+:\s*.*$", linha) is not None

    def _parse_target(self, linha: str):
        nome, resto = linha.split(":", 1)
        nome_target = nome.strip()

        dependencias = [
            dep.strip()
            for dep in resto.strip().split()
            if dep.strip()
        ]

        return nome_target, dependencias

    def _eh_comando(self, linha_original: str) -> bool:
        return linha_original.startswith("\t") or linha_original.startswith("    ")


class BatGenerator:
    def __init__(self, variaveis: dict, targets: dict):
        self.variaveis = variaveis
        self.targets = targets

    def gerar(self) -> str:
        linhas = []

        linhas.extend(self._cabecalho())
        linhas.extend(self._variaveis())
        linhas.extend(self._validacao_argumento())
        linhas.extend(self._roteamento_targets())
        linhas.extend(self._targets())
        linhas.extend(self._exit())

        return "\n".join(linhas)

    def _cabecalho(self):
        return [
            "@echo off",
            "setlocal",
            "",
            ":: Arquivo gerado automaticamente pelo simple-make",
            ""
        ]

    def _variaveis(self):
        linhas = []

        if not self.variaveis:
            return linhas

        linhas.append(":: Variaveis do Makefile")

        for nome, valor in self.variaveis.items():
            linhas.append(f'set "{nome}={valor}"')

        linhas.append("")
        return linhas

    def _validacao_argumento(self):
        linhas = [
            ":: Verifica se foi informado um target",
            'if "%~1"=="" (',
            "    echo Uso: simple-make.bat TARGET",
            "    echo.",
            "    echo Targets disponiveis:"
        ]

        for target in self.targets:
            linhas.append(f"    echo   {target}")

        linhas.extend([
            "    goto exit",
            ")",
            ""
        ])

        return linhas

    def _roteamento_targets(self):
        linhas = [
            ":: Roteamento de targets"
        ]

        for target in self.targets:
            label = self._normalizar_label(target)
            linhas.append(f'if /I "%~1"=="{target}" goto {label}')

        linhas.extend([
            "",
            "echo Target invalido: %~1",
            "goto exit",
            ""
        ])

        return linhas

    def _targets(self):
        linhas = [
            ":: Targets convertidos do Makefile"
        ]

        for nome_target, dados_target in self.targets.items():
            label = self._normalizar_label(nome_target)
            dependencias = dados_target["dependencias"]
            comandos = dados_target["comandos"]

            linhas.append(f":{label}")

            for dependencia in dependencias:
                if dependencia in self.targets:
                    label_dependencia = self._normalizar_label(dependencia)
                    linhas.append(f"    call :{label_dependencia}")

            if comandos:
                for comando in comandos:
                    comando_convertido = self._converter_comando(comando)
                    linhas.append(f"    {comando_convertido}")
            else:
                linhas.append("    rem Target sem comandos")

            linhas.append("goto exit")
            linhas.append("")

        return linhas

    def _exit(self):
        return [
            ":exit",
            "echo simple-make[]: exiting.",
            "endlocal"
        ]

    def _converter_comando(self, comando: str) -> str:
        comando = self._converter_variaveis_parenteses(comando)
        comando = self._converter_variaveis_chaves(comando)
        return comando

    def _converter_variaveis_parenteses(self, comando: str) -> str:
        return re.sub(
            r"\$\(([A-Za-z_][A-Za-z0-9_]*)\)",
            r"%\1%",
            comando
        )

    def _converter_variaveis_chaves(self, comando: str) -> str:
        return re.sub(
            r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
            r"%\1%",
            comando
        )

    def _normalizar_label(self, target: str) -> str:
        label = re.sub(r"[^A-Za-z0-9_]", "_", target)
        return f"target_{label}"


def main():
    caminho_makefile = Path(sys.argv[1]) if len(sys.argv) > 1 else MAKEFILE_PADRAO
    caminho_saida = Path(sys.argv[2]) if len(sys.argv) > 2 else BAT_SAIDA_PADRAO

    if not caminho_makefile.exists():
        print(f"Erro: Makefile nao encontrado: {caminho_makefile}")
        sys.exit(1)

    try:
        parser = MakefileParser(caminho_makefile)
        variaveis, targets = parser.parse()

        if not targets:
            print("Erro: nenhum target encontrado no Makefile.")
            sys.exit(1)

        gerador = BatGenerator(variaveis, targets)
        conteudo_bat = gerador.gerar()

        caminho_saida.write_text(conteudo_bat, encoding="utf-8")

        print(f"Arquivo gerado: {caminho_saida}")
        print("Targets encontrados:")

        for target in targets:
            print(f"  - {target}")

    except SyntaxError as erro:
        print(f"Erro de sintaxe: {erro}")
        sys.exit(1)


if __name__ == "__main__":
    main()
