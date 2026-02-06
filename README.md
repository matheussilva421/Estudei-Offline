# 📚 Estudei Offline

Uma aplicação desktop para gerenciamento de estudos, desenvolvida com **Python** e **Flet**.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-0.80+-purple?logo=flutter&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Funcionalidades

### 📊 Dashboard
- Estatísticas de tempo de estudo
- Indicador de desempenho em questões
- Heatmap de consistência
- Lembretes e atividades recentes

### 📝 Planos de Estudo
- Criação de planos para concursos/provas
- Associação de disciplinas aos planos
- Acompanhamento de progresso

### 📖 Disciplinas
- Cadastro com cores personalizadas
- Gerenciamento de tópicos/edital
- Progresso automático

### 📋 Simulados
- Registro de simulados por disciplina
- Cálculo automático de pontuação
- Histórico completo

### ⏱️ Cronômetro
- Timer overlay para sessões de estudo
- Registro automático no histórico

### 🔔 Revisões & Lembretes
- Sistema de revisão espaçada
- Status: Programadas, Atrasadas, Concluídas, Ignoradas

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.11 ou superior
- pip

### Passos

```bash
# Clone o repositório
git clone https://github.com/matheussilva421/Estudei-Offline.git
cd Estudei-Offline

# Instale as dependências
pip install flet

# Execute o aplicativo
python main.py
```

Ou simplesmente execute o arquivo `Iniciar.bat` no Windows.

---

## 📁 Estrutura do Projeto

```
Estudei-Offline/
├── main.py                 # Ponto de entrada
├── Iniciar.bat             # Script de inicialização (Windows)
├── src/
│   ├── theme.py            # Tema e cores do app
│   ├── components/         # Componentes reutilizáveis
│   │   ├── sidebar.py
│   │   ├── study_modal.py
│   │   ├── mock_exam_modal.py
│   │   ├── timer_overlay.py
│   │   └── ...
│   ├── pages/              # Páginas da aplicação
│   │   ├── dashboard.py
│   │   ├── plans.py
│   │   ├── subjects.py
│   │   ├── mock_exams.py
│   │   └── ...
│   └── data/               # Camada de dados
│       ├── database.py     # Gerenciador SQLite
│       └── crud.py         # Operações CRUD
└── tests/
    └── test_crud.py        # Testes unitários
```

---

## 🧪 Testes

Execute os testes unitários com pytest:

```bash
pip install pytest
python -m pytest tests/test_crud.py -v
```

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|:-----------|:----|
| **Python 3.11** | Linguagem principal |
| **Flet** | Framework de UI multiplataforma |
| **SQLite** | Banco de dados local |
| **pytest** | Testes automatizados |

---

## 📸 Screenshots

*Em breve*

---

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie sua feature branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Matheus Silva**
- GitHub: [@matheussilva421](https://github.com/matheussilva421)

---

⭐ Se este projeto te ajudou, considere dar uma estrela!
