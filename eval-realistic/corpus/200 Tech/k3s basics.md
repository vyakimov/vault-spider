---
updated: 2026-07-15T12:24:00
id: 01M6E00000000000000000000Q
created: 2026-06-13T09:36:00
---
`curl -sfL https://get.k3s.io | sh -` installs k3s on control plane; on workers run with `K3S_URL=https://cp:6443 K3S_TOKEN=<token>`. Kubeconfig at `/etc/rancher/k3s/k3s.yaml`; copy to local machine with `kubectl --kubeconfig=k3s.yaml get nodes`. Lightweight; built-in containerd and flannel; useful for home labs (runs on RPi).
