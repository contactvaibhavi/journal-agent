export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

brew services restart postgresql

export $(grep -v '^#' .env )
# | xargs -d '\n'

su - postgres -c "psql -c 'CREATE USER \"$POSTGRES_USERNAME\" WITH ENCRYPTED PASSWORD '\''$POSTGRES_PASSWORD'\'';'"
su - postgres -c "psql -c 'ALTER USER \"$POSTGRES_USERNAME\" WITH SUPERUSER;'"
