CREATE TABLE title (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(1024) UNIQUE NOT NULL
);

CREATE TABLE organization (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(1024) UNIQUE NOT NULL
);

CREATE TABLE person (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(1024) NOT NULL,
    title_id UUID REFERENCES title(id),
    organization_id UUID REFERENCES organization(id),
    about TEXT
);
