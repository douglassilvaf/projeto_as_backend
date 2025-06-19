package br.com.universidade.matriculas;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

// @RestController: Diz ao Spring que esta classe é um Controlador REST.
// Isso significa que ela vai lidar com requisições web e retornar dados (como JSON).
@RestController
// @RequestMapping: Define o endereço base para todos os métodos dentro desta classe.
// Todas as requisições para "/api/matriculas" virão para cá.
@RequestMapping("/api/matriculas")
public class MatriculaController {

    // @Autowired: Esta é a "Injeção de Dependência". Pedimos ao Spring:
    // "Por favor, me dê uma instância funcional do MatriculaRepository".
    // O Spring a entrega para nós, pronta para ser usada.
    @Autowired
    private MatriculaRepository matriculaRepository;

    // @PostMapping: Mapeia este método para requisições do tipo POST.
    // Requisições POST são usadas para CRIAR novos recursos.
    @PostMapping
    public ResponseEntity<Matricula> criarMatricula(@RequestBody Matricula novaMatricula) {
        // @RequestBody: Pega o corpo da requisição (o JSON enviado pelo bot)
        // e o converte em um objeto da nossa classe Matricula. A mágica acontece
        // porque os nomes dos campos (nome, email, curso) são os mesmos.
        
        // Usa o repositório para salvar a matrícula no banco de dados H2.
        Matricula matriculaSalva = matriculaRepository.save(novaMatricula);
        
        // Retorna uma resposta de sucesso (200 OK) com os dados da matrícula salva
        // (agora incluindo o ID gerado pelo banco).
        return ResponseEntity.ok(matriculaSalva);
    }
}