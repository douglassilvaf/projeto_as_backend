package br.com.universidade.matriculas;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

// @Repository: Identifica esta interface como um componente de repositório gerenciado pelo Spring.
@Repository
public interface MatriculaRepository extends JpaRepository<Matricula, Long> {
    
    // A mágica acontece aqui!
    // Ao estender JpaRepository, nós automaticamente ganhamos vários métodos
    // para interagir com o banco de dados, como:
    // save(), findById(), findAll(), deleteById(), e muitos outros.
    // Não precisamos escrever nada aqui dentro por enquanto.
    
}