test_normal_user_cannot_filter_sensitive_data: Tenta fazer uma busca por e-mail logado como um cliente comum. O teste verifica se a API bloqueia a ação e retorna o erro 403 Forbidden com a mensagem "Acesso negado" (exatamente a regra que criamos hoje).

test_staff_user_can_filter_sensitive_data: Tenta fazer a mesma busca por e-mail, mas logado como administrador. O teste verifica se a API permite a ação e retorna 200 OK.

test_user_can_only_see_own_cart: Cria um carrinho para o Cliente 1 e outro para o Cliente 2. Loga como Cliente 1 e pede a lista de carrinhos. O teste verifica se a API retorna apenas 1 carrinho e se esse carrinho pertence ao Cliente 1 (garantindo que ele não veja o do vizinho).

test_normal_user_cannot_access_financial_transactions: Tenta acessar a rota de transações financeiras como cliente comum. Verifica se a API bloqueia com 403 Forbidden.

test_staff_user_can_access_financial_transactions: Tenta acessar a mesma rota como administrador. Verifica se a API permite com 200 OK.