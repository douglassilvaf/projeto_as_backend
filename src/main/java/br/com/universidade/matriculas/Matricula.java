package br.com.universidade.matriculas;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

// @Entity: Esta anotação mágica transforma nossa simples classe Java 
// em uma tabela no banco de dados que o Spring vai gerenciar.
@Entity
public class Matricula {

    // @Id: Marca o campo 'id' como a chave primária (identificador único) da tabela.
    @Id
    // @GeneratedValue: Pede para o banco de dados gerar o valor do ID automaticamente 
    // toda vez que uma nova matrícula for salva.
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nome;
    private String email;
    private String curso;

    // Getters e Setters: São métodos públicos que permitem que o Spring
    // e outras partes do nosso código acessem e modifiquem os campos
    // (nome, email, etc.) de forma controlada.

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getCurso() {
        return curso;
    }

    public void setCurso(String curso) {
        this.curso = curso;
    }
}