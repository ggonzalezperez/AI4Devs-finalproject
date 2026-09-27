# Recuperar `sudo` en la VM de la demo

> **Lo ejecuta una persona delante de la consola VNC de TrueNAS.** No se puede hacer por SSH:
> precisamente lo que falta es `sudo`, así que no hay forma de elevar privilegios desde dentro.

## El problema

La VM Ubuntu que aloja la demo (`192.168.31.18`) se administra por SSH con clave, y eso basta para el
día a día: `git pull`, `docker compose up`. Pero **no se conoce la contraseña del usuario `german`**,
así que `sudo` pide algo que nadie sabe.

Consecuencia real, no teórica: **la máquina no recibe parches de seguridad de Ubuntu**, y está
publicada en internet a través del túnel. Al entrar por SSH el propio sistema lo recuerda con
*«Es necesario reiniciar el sistema»*.

## Antes de empezar

- **La demo estará caída** unos minutos: hay que reiniciar la VM. No lo hagas mientras alguien la esté
  revisando.
- Los contenedores llevan `restart: unless-stopped`, así que **vuelven solos** al arrancar. El túnel
  se reconecta sin intervención.
- Los datos no corren riesgo: los volúmenes `pgdata` y `media` son independientes del arranque.

## Pasos

### 1. Abrir la consola de la VM

En la interfaz web de TrueNAS: **Virtualization** → la VM de Chispa → botón de pantalla/**VNC**. Se
abre una consola gráfica. A partir de aquí ya no se usa SSH.

### 2. Entrar en el menú de GRUB

Reinicia la VM desde el propio panel de TrueNAS (*Restart*) y, en cuanto arranque, pulsa **`Esc`**
repetidamente en la ventana VNC.

Si el menú no aparece y arranca directo a Ubuntu, repite manteniendo **`Shift`** pulsado durante el
arranque. Con bhyve la ventana de tiempo es corta: empieza a pulsar antes de que aparezca nada.

### 3. Arrancar en modo recuperación

En el menú de GRUB:

1. **Advanced options for Ubuntu**
2. La entrada que termina en **`(recovery mode)`**
3. En el menú azul de recuperación: **`root` — Drop to root shell prompt**
4. `Enter` para confirmar

Ya tienes consola de root **sin pedir contraseña**. Ese es todo el truco: quien controla el arranque
de una máquina controla la máquina.

### 4. Montar el disco en escritura

En recuperación el sistema de ficheros está **en solo lectura**. Sin esto, `passwd` falla:

```bash
mount -o remount,rw /
```

### 5. Comprobar que el usuario puede usar sudo

Antes de cambiar nada, confirma que el problema es la contraseña y no otra cosa:

```bash
groups german
```

Si entre los grupos aparece **`sudo`**, la contraseña es lo único que falta: ve al paso 6.

Si **no** aparece, añádelo, porque cambiar la contraseña no habría servido de nada:

```bash
usermod -aG sudo german
```

### 6. Poner una contraseña nueva

```bash
passwd german
```

Pídela dos veces. No se ve al teclear, es normal. **Guárdala donde guardes las demás en cuanto
salgas**: si se vuelve a perder, hay que repetir todo esto.

### 7. Volver

```bash
sync
reboot
```

`sync` fuerza a escribir en disco antes de reiniciar; sin él, en un arranque de recuperación se puede
perder el cambio.

## Comprobar que funcionó

Desde tu equipo, por SSH como siempre:

```bash
ssh -i ~/.ssh/chispa_vm_key german@192.168.31.18
sudo -v          # pide la contraseña nueva; si no protesta, está resuelto
docker compose -f /opt/chispa/docker-compose.yml ps   # la demo debe estar arriba
```

## Y ahora sí, actualizar

Era el motivo de todo esto:

```bash
sudo apt update
sudo apt upgrade
sudo reboot       # solo si lo pide; los contenedores vuelven solos
```

Después, quita la entrada correspondiente de la tabla de deuda conocida en
[`estado-implementacion.md`](../entrega-2/estado-implementacion.md).

## Si el menú de GRUB no aparece

Alternativa sin modo recuperación, editando el arranque. En el menú de GRUB, con la entrada de Ubuntu
seleccionada, pulsa **`e`**, busca la línea que empieza por `linux`, añade al final:

```
init=/bin/bash
```

y pulsa **`Ctrl+X`** para arrancar. Caes en una consola de root, y desde ahí valen los pasos 4 a 6.
Para salir, `exec /sbin/init` o `reboot -f`.

Este camino es más manual y deja el arranque a medias, así que se prefiere el modo recuperación.
