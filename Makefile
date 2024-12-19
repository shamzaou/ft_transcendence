# ft_transcendence/Makefile

NAME = ft_transcendence

# Переменные
DOCKER_COMPOSE 	= docker-compose -f
COMPOSE_FILE 	= ./srcs/docker-compose.yml


# Запуск всех сервисов
all:
	$(DOCKER_COMPOSE) $(COMPOSE_FILE) up -d

# Пересборка всех сервисов
build:
	$(DOCKER_COMPOSE) $(COMPOSE_FILE) build

# Остановка всех сервисов
down:
	$(DOCKER_COMPOSE) $(COMPOSE_FILE) down

# Перезапуск всех сервисов
re: down build all

# Просмотр логов всех сервисов
logs:
	$(DOCKER_COMPOSE) $(COMPOSE_FILE) logs -f


# Пересборка и перезапуск конкретного сервиса (например, service1)
build-service1:
	$(DOCKER_COMPOSE) build service1

up-service1:
	$(DOCKER_COMPOSE) up -d service1

down-service1:
	$(DOCKER_COMPOSE) down service1

restart-service1: down-service1 build-service1 up-service1


# Очистка
clean: down
	@$(DOCKER_COMPOSE) $(COMPOSE_FILE) rm -f -s -v

fclean:
	@$(DOCKER_COMPOSE) $(COMPOSE_FILE) down --rmi all -v --remove-orphans

# run-database: check_docker
# 	$(DOCKER_COMPOSE) exec -it postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

# # change users in selct to table name for usernames
# show-users: check_docker
# 	$(DOCKER_COMPOSE) exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "SELECT * FROM users" 

# Задачи
.PHONY: build up down re logs