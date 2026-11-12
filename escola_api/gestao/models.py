from django.db import models

class Curso(models.Model):
    nome = models.CharField(max_length=120)
    eixo = models.CharField(max_length=80)

    def __str__(self):
        return self.nome


class Disciplina(models.Model):
    codigo = models.CharField(max_length=6, unique=True, null=True, blank=True)
    nome = models.CharField(max_length=120, null=False, blank=False)
    carga_horaria = models.PositiveIntegerField(help_text='Em horas.', null=False, blank=False)
    descricao = models.CharField(max_length=250, null=True, blank=True)
    ementa = models.TextField(null=True, blank=True)
    capacidade = models.IntegerField()
    ativa = models.BooleanField(default=True, null=False, blank=False)
    criada_em = models.DateTimeField(auto_now_add=True, null=True)

    # Relacionamentos
    curso = models.ForeignKey(
        Curso,
        on_delete=models.RESTRICT,
        related_name="disciplinas",
        null=True, blank=False
    )

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"
