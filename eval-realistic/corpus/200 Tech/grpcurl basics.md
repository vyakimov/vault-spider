---
updated: 2026-04-08T15:15:00
id: 01M6E000000000000000000146
created: 2026-03-06T12:15:00
---
`grpcurl -plaintext localhost:50051 list` enumerates gRPC services. `grpcurl -plaintext -d '{"id":1}' localhost:50051 package.Service/Method` makes a call. Requires server reflection enabled; add `-import-path proto/` if importing .proto files.
