import sys

with open('app/routers/webhook.py', 'r', encoding='utf-8') as f:
    content = f.read()

target_logic = """                # ── Estado: Aguardando nova data/hora para reagendamento ──
                if estado_atual == "AGUARDANDO_NOVA_DATA_HORA":
                    # Usa o LLM apenas para extrair data e hora da mensagem do cliente
                    resposta_data_hora = await extrair_data_hora_com_ia(texto_cliente, nome_loja)
                    nova_data = resposta_data_hora.get("data")
                    nova_hora = resposta_data_hora.get("hora")
                    
                    if not nova_data or not nova_hora:
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto="Não consegui identificar a data e horário. 😊 Por favor, informe no formato: *dia/mês às HH:MM* (ex: 25/07 às 14:30)."
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)

                    # Validação: impedir reagendamento para data no passado
                    try:
                        nova_data_obj = datetime.strptime(nova_data, "%Y-%m-%d").date()
                        if nova_data_obj < datetime.now(ZoneInfo("America/Sao_Paulo")).date():
                            enviar_mensagem_whatsapp(
                                numero_destino=telefone_cliente,
                                texto="Não é possível reagendar para uma data que já passou. 😊 Por favor, informe uma data futura."
                            )
                            return JSONResponse(content={"status": "sucesso"}, status_code=200)
                    except ValueError:
                        pass"""

new_logic = """                # ── Estado: Aguardando nova data/hora para reagendamento ──
                if estado_atual == "AGUARDANDO_NOVA_DATA_HORA":
                    resposta_data_hora = await extrair_data_hora_com_ia(texto_cliente, nome_loja)
                    
                    # Recupera data parcial da sessão caso exista
                    nova_data = resposta_data_hora.get("data") or dados_sessao.get("nova_data_parcial")
                    nova_hora = resposta_data_hora.get("hora")
                    
                    if not nova_data and not nova_hora:
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto="Não consegui identificar a data e horário. 😊 Para quando você gostaria de reagendar? (ex: amanhã à tarde, quinta às 15h)"
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)

                    # Validação: impedir reagendamento para data no passado
                    if nova_data:
                        try:
                            nova_data_obj = datetime.strptime(nova_data, "%Y-%m-%d").date()
                            if nova_data_obj < datetime.now(ZoneInfo("America/Sao_Paulo")).date():
                                if "nova_data_parcial" in dados_sessao:
                                    del dados_sessao["nova_data_parcial"]
                                    salvar_sessao_cliente(db, telefone_cliente, schema_alvo, dados_sessao)
                                enviar_mensagem_whatsapp(
                                    numero_destino=telefone_cliente,
                                    texto="Não é possível reagendar para uma data que já passou. 😊 Por favor, informe uma data futura."
                                )
                                return JSONResponse(content={"status": "sucesso"}, status_code=200)
                        except ValueError:
                            pass"""

if target_logic in content:
    content = content.replace(target_logic, new_logic)
    print("Replace 1 successful")
else:
    print("Target 1 not found!")

target_2 = """                        data_obj = datetime.strptime(nova_data, "%Y-%m-%d").date()
                        if str(data_obj.weekday()) in dias_fechados:
                            enviar_mensagem_whatsapp(
                                numero_destino=telefone_cliente,
                                texto="Infelizmente o estabelecimento está fechado neste dia da semana. Que tal reagendarmos para outro dia?"
                            )
                            return JSONResponse(content={"status": "sucesso"}, status_code=200)

                        hora_nova_obj = datetime.strptime(nova_hora, "%H:%M").time()"""

new_2 = """                        data_obj = datetime.strptime(nova_data, "%Y-%m-%d").date()
                        if str(data_obj.weekday()) in dias_fechados:
                            if "nova_data_parcial" in dados_sessao:
                                del dados_sessao["nova_data_parcial"]
                                salvar_sessao_cliente(db, telefone_cliente, schema_alvo_seguro, dados_sessao)
                            enviar_mensagem_whatsapp(
                                numero_destino=telefone_cliente,
                                texto="Infelizmente o estabelecimento está fechado neste dia da semana. Que tal reagendarmos para outro dia?"
                            )
                            return JSONResponse(content={"status": "sucesso"}, status_code=200)

                        horarios_ocup = []
                        for ag in ags_dia_reag:
                            ag_ini = ag["horario_agendamento"]
                            if isinstance(ag_ini, str):
                                ag_ini = datetime.strptime(ag_ini, "%H:%M").time()
                            ag_fim = (datetime.combine(datetime.today(), ag_ini) + timedelta(minutes=ag["dur"])).time()
                            horarios_ocup.append((ag_ini, ag_fim))

                        h_abre_r = merchant_config_reag.horario_abertura if merchant_config_reag else "08:00"
                        h_fecha_r = merchant_config_reag.horario_fechamento if merchant_config_reag else "18:00"
                        abertura_r = datetime.strptime(h_abre_r, "%H:%M").time()
                        fechamento_r = datetime.strptime(h_fecha_r, "%H:%M").time()

                        slots_livres = []
                        cursor_r = datetime.combine(datetime.today(), abertura_r)
                        fecha_r = datetime.combine(datetime.today(), fechamento_r)

                        while cursor_r + timedelta(minutes=duracao_reag) <= fecha_r:
                            s_ini = cursor_r.time()
                            s_fim = (cursor_r + timedelta(minutes=duracao_reag)).time()
                            livre = True
                            if not permite_sobreposicao_reag:
                                livre = all(not (s_ini < oc_fim and s_fim > oc_ini) for oc_ini, oc_fim in horarios_ocup)
                            if livre and almoco_inicio and almoco_fim:
                                if s_ini < almoco_fim and s_fim > almoco_inicio:
                                    livre = False
                            
                            if livre:
                                # Se for hoje, só sugerir horários futuros
                                if data_obj == datetime.now(ZoneInfo("America/Sao_Paulo")).date():
                                    if s_ini > datetime.now(ZoneInfo("America/Sao_Paulo")).time():
                                        slots_livres.append(s_ini.strftime("%H:%M"))
                                else:
                                    slots_livres.append(s_ini.strftime("%H:%M"))
                            cursor_r += timedelta(minutes=30)

                        if nova_data and not nova_hora:
                            dados_sessao["nova_data_parcial"] = nova_data
                            salvar_sessao_cliente(db, telefone_cliente, schema_alvo_seguro, dados_sessao)
                            
                            if not slots_livres:
                                enviar_mensagem_whatsapp(
                                    numero_destino=telefone_cliente,
                                    texto=f"Infelizmente não há horários livres no dia {nova_data_obj.strftime('%d/%m')}. Que tal escolher outra data?"
                                )
                            else:
                                sugestoes_livres = "*, *".join(slots_livres[:3])
                                enviar_mensagem_whatsapp(
                                    numero_destino=telefone_cliente,
                                    texto=f"Entendi que é para o dia {nova_data_obj.strftime('%d/%m')}. Quais destes horários você prefere? Temos livres: *{sugestoes_livres}*"
                                )
                            return JSONResponse(content={"status": "sucesso"}, status_code=200)

                        hora_nova_obj = datetime.strptime(nova_hora, "%H:%M").time()"""

if target_2 in content:
    content = content.replace(target_2, new_2)
    print("Replace 2 successful")
else:
    print("Target 2 not found!")

target_3 = """                        if conflito_reag:
                            horarios_ocup = []
                            for ag in ags_dia_reag:
                                ag_ini = ag["horario_agendamento"]
                                if isinstance(ag_ini, str):
                                    ag_ini = datetime.strptime(ag_ini, "%H:%M").time()
                                ag_fim = (datetime.combine(datetime.today(), ag_ini) + timedelta(minutes=ag["dur"])).time()
                                horarios_ocup.append((ag_ini, ag_fim))

                            h_abre_r = merchant_config_reag.horario_abertura if merchant_config_reag else "08:00"
                            h_fecha_r = merchant_config_reag.horario_fechamento if merchant_config_reag else "18:00"
                            abertura_r = datetime.strptime(h_abre_r, "%H:%M").time()
                            fechamento_r = datetime.strptime(h_fecha_r, "%H:%M").time()

                            slots_antes, slots_depois = [], []
                            cursor_r = datetime.combine(datetime.today(), abertura_r)
                            fecha_r = datetime.combine(datetime.today(), fechamento_r)
                            hora_nova_dt = datetime.combine(datetime.today(), hora_nova_obj)

                            while cursor_r + timedelta(minutes=duracao_reag) <= fecha_r:
                                s_ini = cursor_r.time()
                                s_fim = (cursor_r + timedelta(minutes=duracao_reag)).time()
                                livre = all(
                                    not (s_ini < oc_fim and s_fim > oc_ini)
                                    for oc_ini, oc_fim in horarios_ocup
                                )
                                if livre and almoco_inicio and almoco_fim:
                                    if s_ini < almoco_fim and s_fim > almoco_inicio:
                                        livre = False
                                
                                if livre:
                                    if cursor_r < hora_nova_dt:
                                        slots_antes.append(s_ini.strftime("%H:%M"))
                                    else:
                                        slots_depois.append(s_ini.strftime("%H:%M"))
                                cursor_r += timedelta(minutes=30)

                            sugestao_antes = slots_antes[-1] if slots_antes else None
                            sugestao_depois = slots_depois[0] if slots_depois else None
                            sugestoes_reag = [s for s in [sugestao_antes, sugestao_depois] if s]

                            msg_conflito_reag = f"Poxa, o horário das {nova_hora} já está ocupado nessa data. 😊 "
                            if len(sugestoes_reag) == 2:
                                msg_conflito_reag += f"Tenho disponibilidade às *{sugestoes_reag[0]}* ou às *{sugestoes_reag[1]}*. Qual você prefere?"
                            elif len(sugestoes_reag) == 1:
                                msg_conflito_reag += f"O horário mais próximo disponível é às *{sugestoes_reag[0]}*. Podemos reagendar para esse horário?"
                            else:
                                msg_conflito_reag += "Infelizmente não há mais horários disponíveis nesse dia. Que tal outra data?"

                            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=msg_conflito_reag)
                            return JSONResponse(content={"status": "sucesso"}, status_code=200)"""

new_3 = """                        if conflito_reag:
                            # Tira a hora da sessão pra forçar perguntar de novo
                            if "nova_data_parcial" not in dados_sessao:
                                dados_sessao["nova_data_parcial"] = nova_data
                            salvar_sessao_cliente(db, telefone_cliente, schema_alvo_seguro, dados_sessao)

                            slots_antes = [s for s in slots_livres if datetime.strptime(s, "%H:%M").time() < hora_nova_obj]
                            slots_depois = [s for s in slots_livres if datetime.strptime(s, "%H:%M").time() > hora_nova_obj]
                            
                            sugestao_antes = slots_antes[-1] if slots_antes else None
                            sugestao_depois = slots_depois[0] if slots_depois else None
                            sugestoes_reag = [s for s in [sugestao_antes, sugestao_depois] if s]

                            msg_conflito_reag = f"Poxa, o horário das {nova_hora} já está ocupado nessa data. 😊 "
                            if len(sugestoes_reag) == 2:
                                msg_conflito_reag += f"Tenho disponibilidade às *{sugestoes_reag[0]}* ou às *{sugestoes_reag[1]}*. Qual você prefere?"
                            elif len(sugestoes_reag) == 1:
                                msg_conflito_reag += f"O horário mais próximo disponível é às *{sugestoes_reag[0]}*. Podemos reagendar para esse horário?"
                            else:
                                msg_conflito_reag += "Infelizmente não há mais horários disponíveis nesse dia. Que tal outra data?"

                            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=msg_conflito_reag)
                            return JSONResponse(content={"status": "sucesso"}, status_code=200)"""

if target_3 in content:
    content = content.replace(target_3, new_3)
    print("Replace 3 successful")
else:
    print("Target 3 not found!")


target_4 = """                    db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                    ag_id_alvo = dados_sessao.get("agendamento_id_alvo")"""

new_4 = """                    db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                    
                    # Se deu tudo certo, limpa a memória parcial
                    if "nova_data_parcial" in dados_sessao:
                        del dados_sessao["nova_data_parcial"]
                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo_seguro, dados_sessao)
                        
                    ag_id_alvo = dados_sessao.get("agendamento_id_alvo")"""

if target_4 in content:
    content = content.replace(target_4, new_4)
    print("Replace 4 successful")
else:
    print("Target 4 not found!")

with open('app/routers/webhook.py', 'w', encoding='utf-8') as f:
    f.write(content)
