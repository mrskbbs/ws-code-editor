# build stage
FROM golang:alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /dockerproxy

# runtime
FROM scratch AS runtime
WORKDIR /runtime
COPY --from=build /dockerproxy /dockerproxy
EXPOSE 1337
ENTRYPOINT ["/dockerproxy"]
