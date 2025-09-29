# proxy_tads
Alunos: José Paulo Liossi, Vinicius Carneiro de Aguiar

Para rodar no windowns:

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload

Para testar:
via terminal:
python teste_proxy.py

ou acesse: 
(http://127.0.0.1:8000/docs#/) 
*para acessar a api de cache (que mostra as requisições já feitas é necessário clicar em executar)