```mermaid
graph TD;
    subgraph "1. 属性字典 (The Dictionary)"
        A["<b>Attribute (3)</b><br/>属性<br/>e.g., 颜色, 存储容量"]
        AV["<b>AttributeValue (4)</b><br/>属性值<br/>e.g., 蓝色, 256GB"]
    end

    subgraph "2. 产品模板 (The Template)"
        SPU["<b>SPU (5)</b><br/>SPU产品单元<br/>e.g., iPhone 15 Pro"]
        SPUA["<b>SPUAttribute (6)</b><br/>(中间表)"]
    end
    
    subgraph "3. 具体商品 (The Instance)"
        SKU["<b>SKU (7)</b><br/>库存量单位<br/>e.g., 蓝色, 256GB的iPhone"]
        SKUAV["<b>SKUAttributeValue (8)</b><br/>(中间表)"]
    end

    style A fill:#e3f2fd,stroke:#333
    style AV fill:#e3f2fd,stroke:#333
    style SPU fill:#e8f5e9,stroke:#333
    style SPUA fill:#e8f5e9,stroke:#333
    style SKU fill:#fff3e0,stroke:#333
    style SKUAV fill:#fff3e0,stroke:#333

    A --> AV;
    
    SPU -- "定义规格范围" --> SPUA;
    SPUA -- "从字典中选择<b>属性</b>" --> A;
    
    SKU -- "是...的一个实例" --> SPU;
    SKU -- "为规格赋值" --> SKUAV;
    SKUAV -- "从字典中选择<b>属性值</b>" --> AV;
    SKUAV -- "指定哪个属性" --> A;