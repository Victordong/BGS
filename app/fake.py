from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import Operator, Accuchek, Bed, Data, Patient, BedHistory, SpareData
from datetime import datetime

def man_patients(count=50):
    # hospital = "空军总院",
    # office = "牙科",
    # lesion = "北京",
    # operator_name = "admin",
    # tel = "15810058975",
    # mail = "1468767640",
    # operator = Operator(hospital=hospital, office=office, lesion=lesion, operator_name=operator_name, tel=tel,
    #                     mail=mail)
    # operator.password = 'root'
    # db.session.add(operator)
    # db.session.commit()
    fake = Faker(locale='zh_CN')
    i = 0
    operator_count = Operator.query.count()
    while i < count:
        p = Patient(
            patient_name=fake.name(),
            sex = "男",
            tel = fake.phone_number(),
            id_number = fake.phone_number(),
            age = randint(20, 80),
            doctor_name = fake.name()
        )
        db.session.add(p)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def woman_patients(count=50):
    fake = Faker(locale='zh_CN')
    i = 0
    while i < count:
        p = Patient(
            patient_name=fake.name(),
            sex="女",
            tel=fake.phone_number(),
            id_number=fake.phone_number(),
            age=randint(20, 80),
            doctor_name=fake.name()
        )
        db.session.add(p)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def accucheks(count=112):
    fake = Faker(locale='zh_CN')
    i = 1
    p_count = Patient.query.count()
    while i <count+1:
        p = Patient.query.offset(randint(0, p_count - 1)).first()
        a = Accuchek(
            bed_id=i,
            sn = fake.phone_number()
        )
        db.session.add(a)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

        b = Bed(
            patient_id = p.patient_id,
            sn = a.sn
        )
        db.session.add(b)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

def datas(count=1000):
    fake = Faker(locale='zh_CN')
    i=0
    a_count = Accuchek.query.count()
    p_count = Patient.query.count()
    while i<count:
        p = Patient.query.offset(randint(0, p_count-1)).first()
        a = Accuchek.query.offset(randint(0, a_count-1)).first()
        d = Data(
            sn = a.sn,
            time = fake.time(),
            date = datetime.utcnow().date(),
            id_number=p.id_number,
            patient_id = p.patient_id,
            glucose=randint(10, 20)
        )
        db.session.add(d)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def guard_datas(count=200):
    fake = Faker(locale='zh_CN')
    i = 0
    while i<count:
        d = SpareData(
            sn = '00000000',
            time=fake.time(),
            date=datetime.utcnow().date(),
            glucose=randint(10,20)
        )
        db.session.add(d)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()
    i = 0
    while i <count:
        d = SpareData(
            sn = '000000000',
            time=fake.time(),
            date=datetime.utcnow().date(),
            glucose=randint(10, 20),
            id_number = fake.phone_number(),
            patient_name=fake.name(),
            sex = 'nan',
            age = randint(20, 60),
            doctor=fake.name()
        )
        db.session.add(d)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()
    i = 0
    while i<count:
        d = SpareData(
            sn = '11111111',
            time=fake.time(),
            date=datetime.utcnow().date(),
            glucose=randint(10,20)
        )
        db.session.add(d)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()
    i = 0
    while i <count:
        d = SpareData(
            sn = '11111111',
            time=fake.time(),
            date=datetime.utcnow().date(),
            glucose=randint(10, 20),
            id_number = fake.phone_number(),
            patient_name=fake.name(),
            sex = 'nan',
            age = randint(20, 60),
            doctor=fake.name()
        )
        db.session.add(d)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()